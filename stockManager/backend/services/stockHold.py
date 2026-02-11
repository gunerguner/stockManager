"""
持仓计算模块
提供股票持仓计算相关功能
"""
from typing import Dict, List
import datetime

from ..models import Operation
from ..common.constants import OperationType


class StockHold:
    """持仓计算服务类，负责处理股票持仓相关计算"""
    
    @classmethod
    def get_holding_stocks(cls, operation_list: Dict[str, List[Operation]], target_date: datetime.date = None) -> List[str]:
        """获取指定日期持有的股票代码列表"""
        if target_date is None:
            target_date = datetime.date.today()
        
        holding_stocks = []
        
        for code, operations in operation_list.items():
            if not operations:
                continue
            
            sorted_operations = sorted(operations, key=lambda op: op.date)
            current_hold = cls.calculate_hold_count_at_date(sorted_operations, target_date)
            
            if current_hold > 0:
                holding_stocks.append(code)
        
        return holding_stocks
    
    @classmethod
    def calculate_hold_count_at_date(cls, operations: List[Operation], target_date: datetime.date) -> float:
        """计算到指定日期时的持仓数"""
        current_hold = 0.0
        for operation in operations:
            if operation.date > target_date:
                break
            
            if operation.operationType == OperationType.BUY:
                current_hold += operation.count
            elif operation.operationType == OperationType.SELL:
                current_hold -= operation.count
            elif operation.operationType == OperationType.DIVIDEND:
                dividend_multiplier = operation.reserve + operation.stock
                current_hold += current_hold * dividend_multiplier
        
        return current_hold
