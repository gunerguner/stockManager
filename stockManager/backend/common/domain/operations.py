"""Operation 类型相关的共享计算逻辑"""
import datetime

from backend.common.constants import OperationType
from backend.common.domain.settlement import (
    buy_outflow_cny,
    dividend_cash_cny,
    sell_inflow_cny,
)
from backend.models import Operation


def dividend_multiplier(operation: Operation) -> float:
    """除权除息送股/转增合计乘数（reserve + stock）"""
    return operation.reserve + operation.stock


def hold_count_before(
    operations: list[Operation],
    *,
    on_date: datetime.date,
    sort_order: int,
    exclude_pk: int | None = None,
    append_same_day: bool = False,
) -> int:
    """插入点之前的持股，向 0 取整。

    append_same_day 用于新建且同日顺序仍为 0：与保存时自动排到当天最后一致，
    当天已有记录都算在本条之前。
    """
    hold = 0.0
    for operation in operations:
        if exclude_pk is not None and operation.pk == exclude_pk:
            continue
        if not _is_before_insertion(
            operation,
            on_date=on_date,
            sort_order=sort_order,
            exclude_pk=exclude_pk,
            append_same_day=append_same_day,
        ):
            continue
        hold = apply_operation_to_hold(hold, operation)
    return int(hold)


def _is_before_insertion(
    operation: Operation,
    *,
    on_date: datetime.date,
    sort_order: int,
    exclude_pk: int | None,
    append_same_day: bool,
) -> bool:
    if operation.date > on_date:
        return False
    if operation.date < on_date or append_same_day:
        return True
    if operation.sortOrder != sort_order:
        return operation.sortOrder < sort_order
    # 新建记录尚无主键，同顺序的已有记录会排在它前面
    if exclude_pk is None:
        return True
    return (operation.pk or 0) < exclude_pk


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


def operation_cash_delta_cny(operation: Operation, current_hold: float) -> float:
    """人民币现金变动：买入流出为负，卖出/分红流入为正。"""
    match operation.operationType:
        case OperationType.BUY:
            return -buy_outflow_cny(operation)
        case OperationType.SELL:
            return sell_inflow_cny(operation)
        case OperationType.DIVIDEND:
            return dividend_cash_cny(operation, current_hold)
        case _:
            return 0.0


def apply_net_invested(
    net_invested: float,
    current_hold: float,
    operation: Operation,
) -> tuple[float, float]:
    """按人民币资金账本更新净占用资金与持股数（供资金加权 / XIRR 口径）。"""
    # 现金流入减少净投入，流出增加净投入
    net_invested -= operation_cash_delta_cny(operation, current_hold)
    current_hold = apply_operation_to_hold(current_hold, operation)
    return net_invested, current_hold
