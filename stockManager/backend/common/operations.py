"""Operation 类型相关的共享计算逻辑"""
from backend.models import Operation
from backend.common.constants import OperationType


def dividend_multiplier(operation: Operation) -> float:
    """除权除息送股/转增合计乘数（reserve + stock）"""
    return operation.reserve + operation.stock


def apply_operation_to_hold(hold: float, operation: Operation) -> float:
    """按操作类型更新持股数"""
    match operation.operationType:
        case OperationType.BUY:
            return hold + operation.count
        case OperationType.SELL:
            return hold - operation.count
        case OperationType.DIVIDEND:
            return hold + hold * dividend_multiplier(operation)
        case _:
            return hold


def apply_net_invested(
    net_invested: float,
    current_hold: float,
    operation: Operation,
) -> tuple[float, float]:
    """按 overall_sum 规则更新净占用资金与持股数"""
    match operation.operationType:
        case OperationType.BUY:
            net_invested += operation.count * operation.price + operation.fee
        case OperationType.SELL:
            net_invested -= operation.count * operation.price - operation.fee
        case OperationType.DIVIDEND:
            net_invested -= current_hold * operation.cash
    current_hold = apply_operation_to_hold(current_hold, operation)
    return net_invested, current_hold
