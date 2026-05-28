"""持仓计算模块
提供股票持仓计算相关功能
"""
import datetime

from ..models import Operation
from ..common.operations import apply_operation_to_hold
from ..common.types import OperationDict
from ..common.utils import operation_sort_key


class StockHold:
    """持仓计算服务类，负责处理股票持仓相关计算"""
    
    @classmethod
    def get_holding_stocks(cls, operation_list: OperationDict, target_date: datetime.date = None) -> list[str]:
        """获取指定日期持有的股票代码列表"""
        if target_date is None:
            target_date = datetime.date.today()

        return [
            code
            for code, operations in operation_list.items()
            if operations
            and cls.calculate_hold_count_at_date(
                sorted(operations, key=operation_sort_key),
                target_date,
            ) > 0
        ]
    
    @classmethod
    def calculate_hold_count_at_date(cls, operations: list[Operation], target_date: datetime.date) -> float:
        """计算到指定日期时的持仓数"""
        current_hold = 0.0
        for operation in operations:
            if operation.date > target_date:
                break
            current_hold = apply_operation_to_hold(current_hold, operation)
        return current_hold
