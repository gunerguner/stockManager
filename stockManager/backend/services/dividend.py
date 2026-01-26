"""
分红服务模块
提供股票分红数据查询和处理功能
"""
from typing import Dict, List
import datetime

import baostock as bs

from ..common import logger
from ..common.constants import OperationType
from ..common.utils import safe_float
from ..models import Operation
from django.contrib.auth.models import User

class Dividend:
    """分红服务类，负责处理股票分红相关操作（纯工具类，无状态）"""
    
    @classmethod
    def generate_dividend(cls, user: User, operation_list: Dict[str, List[Operation]]) -> List[str]:
        """为持有的股票生成分红数据"""
        holding_stocks = cls._get_holding_stocks(operation_list)
        updated_codes = []
        
        try:
            bs.login()
            for code in holding_stocks:
                operations = operation_list[code]
                updated_code = cls._generate_dividend_single(user, code, operations)
                if updated_code:
                    updated_codes.append(updated_code)
        finally:
            bs.logout()
        
        return updated_codes
    
    @classmethod
    def _get_holding_stocks(cls, operation_list: Dict[str, List[Operation]]) -> List[str]:
        """获取当前持有的股票代码列表"""
        today = datetime.date.today()
        holding_stocks = []
        
        for code, operations in operation_list.items():
            # 按日期排序操作列表，确保计算持仓数时顺序正确
            sorted_operations = sorted(operations, key=lambda op: op.date)
            # 使用统一的方法计算今天的持股数
            current_hold = cls._calculate_hold_count_at_date(sorted_operations, today)
            
            if current_hold > 0:
                holding_stocks.append(code)
        
        return holding_stocks
    
    @classmethod
    def _calculate_hold_count_at_date(cls, operations: List[Operation], target_date: datetime.date) -> float:
        """计算到指定日期时的持仓数"""
        current_hold = 0.0
        for operation in operations:
            # 只处理目标日期之前的操作
            if operation.date > target_date:
                break
            
            if operation.operationType == OperationType.BUY:
                current_hold += operation.count
            elif operation.operationType == OperationType.SELL:
                current_hold -= operation.count
            elif operation.operationType == OperationType.DIVIDEND:
                # 分红操作：送股和转增会增加持股数
                dividend_multiplier = operation.reserve + operation.stock
                current_hold += current_hold * dividend_multiplier
        
        return current_hold

    @classmethod
    def _generate_dividend_single(cls, user: User, code: str, operations: List[Operation]) -> str:
        """生成个股除权除息信息"""
        if not operations:
            return ""

        try:
            today = datetime.date.today()
            update_count = 0

            exist_dv_operations = [op for op in operations if op.operationType == OperationType.DIVIDEND]
            date_set = {str(op.date) for op in exist_dv_operations}

            first_year = operations[0].date.year
            year_now = today.year
            formatted_code = f"{code[:2]}.{code[2:]}"

            # 按日期排序操作列表，确保计算持仓数时顺序正确
            sorted_operations = sorted(operations, key=lambda op: op.date)

            for year in range(first_year, year_now + 1):
                try:
                    result_set = bs.query_dividend_data(code=formatted_code, year=str(year), yearType="operate")
                    
                    while result_set.error_code == "0" and result_set.next():
                        data = result_set.get_row_data()
                        dividend_date_str = data[6]
                        
                        # 解析分红日期
                        try:
                            dividend_date = datetime.datetime.strptime(dividend_date_str, '%Y-%m-%d').date()
                        except (ValueError, TypeError) as e:
                            logger.warning(f"分红日期格式解析失败: {dividend_date_str}, 错误: {e}")
                            continue
                        
                        # 检查是否已有同一天的除权记录
                        if dividend_date_str in date_set:
                            continue
                        
                        # 计算到分红日期时的持仓数
                        hold_count_at_date = cls._calculate_hold_count_at_date(sorted_operations, dividend_date)
                        
                        # 只有在有持仓时才插入分红记录
                        if hold_count_at_date > 0:
                            cash = safe_float(data[9])
                            reserve = safe_float(data[11])
                            stock = safe_float(data[13])
                            
                            Operation.objects.create(
                                user=user,
                                date=dividend_date,
                                code=code,
                                operationType=OperationType.DIVIDEND,
                                cash=cash,
                                reserve=reserve,
                                stock=stock,
                                count=hold_count_at_date,  # 设置当时的持仓数
                            )
                            update_count += 1
                            date_set.add(dividend_date_str)
                            
                except Exception as e:
                    logger.error(f"查询股票 {code} 第 {year} 年分红数据失败: {e}")
                    continue

            return code if update_count > 0 else ""
            
        except Exception as e:
            logger.error(f"生成股票 {code} 分红信息失败: {e}")
            return ""

