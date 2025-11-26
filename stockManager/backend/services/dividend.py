"""
分红服务模块
提供股票分红数据查询和处理功能
"""
from typing import List, Optional
import datetime

import baostock as bs

from ..common import logger
from ..common.constants import OperationType
from ..models import Operation
from ..utils import _safe_float
from django.contrib.auth.models import User

DIVIDEND_DATE_CHECK_RANGE = 5  # 分红日期检查范围（前后天数）


class Dividend:
    """分红服务类，负责处理股票分红相关操作（纯工具类，无状态）"""
    
    @classmethod
    def generate_dividend(cls, user: User, operation_list: dict) -> List[str]:
        """为持有的股票生成分红数据"""
        holding_stocks = cls._get_holding_stocks(operation_list)
        updated_codes = []
        
        try:
            bs.login()
            for code in holding_stocks:
                updated_code = cls._generate_dividend_single(user, operation_list, code)
                if updated_code:
                    updated_codes.append(updated_code)
        finally:
            bs.logout()
        
        return updated_codes
    
    @classmethod
    def _get_holding_stocks(cls, operation_list: dict) -> List[str]:
        """获取当前持有的股票代码列表"""
        from .calculator import Calculator
        return Calculator.get_holding_stocks(operation_list)
    
    @classmethod
    def _is_date_near_existing(cls, date_str: str, existing_dates: set, today: datetime.date) -> bool:
        """检查日期是否在已有日期列表中,或在已有日期的前后指定天数范围内"""
        if date_str in existing_dates:
            return True
        
        try:
            current_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            if current_date > today:
                return True
            
            for days_offset in range(1, DIVIDEND_DATE_CHECK_RANGE + 1):
                one_day = datetime.timedelta(days=days_offset)
                previous_day = (current_date - one_day).strftime('%Y-%m-%d')
                next_day = (current_date + one_day).strftime('%Y-%m-%d')
                if previous_day in existing_dates or next_day in existing_dates:
                    return True
            
            return False
        except (ValueError, TypeError) as e:
            logger.warning(f"日期格式解析失败: {date_str}, 错误: {e}")
            return date_str in existing_dates
    
    @classmethod
    def _generate_dividend_single(cls, user: User, operation_list: dict, code: Optional[str]) -> str:
        """生成个股除权除息信息"""
        if code is None:
            return ""

        try:
            today = datetime.date.today()
            update_count = 0
            single_operation_list = operation_list[code]

            exist_dv_operations = [op for op in single_operation_list if op.operationType == OperationType.DIVIDEND]
            date_set = {str(op.date) for op in exist_dv_operations}

            first_year = single_operation_list[0].date.year
            year_now = today.year
            formatted_code = f"{code[:2]}.{code[2:]}"

            for year in range(first_year, year_now + 1):
                try:
                    result_set = bs.query_dividend_data(code=formatted_code, year=str(year), yearType="operate")
                    
                    while result_set.error_code == "0" and result_set.next():
                        data = result_set.get_row_data()
                        dividend_date = data[6]
                        cash = _safe_float(data[9])
                        reserve = _safe_float(data[11])
                        stock = _safe_float(data[13])
     
                        if not cls._is_date_near_existing(dividend_date, date_set, today):
                            Operation.objects.create(
                                user=user,
                                date=dividend_date,
                                code=code,
                                operationType=OperationType.DIVIDEND,
                                cash=cash,
                                reserve=reserve,
                                stock=stock,
                            )
                            update_count += 1
                            date_set.add(dividend_date)
                            
                except Exception as e:
                    logger.error(f"查询股票 {code} 第 {year} 年分红数据失败: {e}")
                    continue

            update_count -= cls._update_dividend_holdings(user, code)
            return code if update_count > 0 else ""
            
        except Exception as e:
            logger.error(f"生成股票 {code} 分红信息失败: {e}")
            return ""
    
    @classmethod
    def _update_dividend_holdings(cls, user: User, code: str) -> int:
        """更新分红记录的持仓数量并删除无效记录"""
        operations = Operation.objects.filter(user=user, code=code).order_by("date")
        current_hold = 0
        deleted_count = 0
        
        for operation in operations:
            if operation.operationType == OperationType.BUY:
                current_hold += operation.count
            elif operation.operationType == OperationType.SELL:
                current_hold -= operation.count
            elif operation.operationType == OperationType.DIVIDEND:
                if current_hold == 0:
                    operation.delete()
                    deleted_count += 1
                else:
                    operation.count = current_hold
                    operation.save()
                    current_hold += current_hold * (operation.reserve + operation.stock)
        
        return deleted_count

