"""Operation 类型相关的共享计算逻辑"""
from ..models import Operation
from .constants import OperationType


def apply_operation_to_hold(hold: float, operation: Operation) -> float:
    """按操作类型更新持股数"""
    match operation.operationType:
        case OperationType.BUY:
            return hold + operation.count
        case OperationType.SELL:
            return hold - operation.count
        case OperationType.DIVIDEND:
            return hold + hold * (operation.reserve + operation.stock)
        case _:
            return hold
