"""资金加权累计收益率计算"""
import datetime

from ...common.constants import OperationType
from ...common.utils import format_percent, operation_sort_key
from ...models import Operation
from .constants import MIN_HOLD_COUNT_THRESHOLD, MIN_VALUE_THRESHOLD


def _apply_net_invested(
    net_invested: float,
    current_hold: float,
    operation: Operation,
) -> tuple[float, float]:
    """按 overall_sum 规则更新净占用资金与持股数"""
    match operation.operationType:
        case OperationType.BUY:
            net_invested += operation.count * operation.price + operation.fee
            current_hold += operation.count
        case OperationType.SELL:
            net_invested -= operation.count * operation.price - operation.fee
            current_hold -= operation.count
        case OperationType.DIVIDEND:
            dividend_multiplier = operation.reserve + operation.stock
            net_invested -= current_hold * operation.cash
            current_hold += current_hold * dividend_multiplier
    return net_invested, current_hold


def calculate_money_weighted_return(
    operations: list[Operation],
    offset_total: float,
) -> str:
    """资金加权累计收益率：offsetTotal / 加权平均占用资金"""
    sorted_ops = sorted(operations, key=operation_sort_key)
    if not sorted_ops:
        return format_percent(0.0)

    start_date = sorted_ops[0].date
    today = datetime.date.today()

    net_invested = 0.0
    current_hold = 0.0
    dollar_days = 0.0
    holding_days = 0.0
    peak_net_invested = 0.0
    total_buy_amount = 0.0
    seg_start = start_date

    for operation in sorted_ops:
        seg_days = (operation.date - seg_start).days
        if seg_days > 0 and current_hold >= MIN_HOLD_COUNT_THRESHOLD:
            dollar_days += max(net_invested, 0.0) * seg_days
            holding_days += seg_days

        net_invested, current_hold = _apply_net_invested(
            net_invested, current_hold, operation
        )
        peak_net_invested = max(peak_net_invested, max(net_invested, 0.0))
        if operation.operationType == OperationType.BUY:
            total_buy_amount += operation.count * operation.price + operation.fee
        seg_start = operation.date

    if current_hold >= MIN_HOLD_COUNT_THRESHOLD:
        effective_end = today
    else:
        effective_end = sorted_ops[-1].date

    tail_days = (effective_end - seg_start).days
    if tail_days > 0 and current_hold >= MIN_HOLD_COUNT_THRESHOLD:
        dollar_days += max(net_invested, 0.0) * tail_days
        holding_days += tail_days

    total_holding_days = max(holding_days, 0.0)
    if total_holding_days >= MIN_VALUE_THRESHOLD:
        adjusted_begin = dollar_days / total_holding_days
    else:
        adjusted_begin = peak_net_invested
        if adjusted_begin < MIN_VALUE_THRESHOLD:
            adjusted_begin = total_buy_amount
    if adjusted_begin < MIN_VALUE_THRESHOLD:
        return format_percent(0.0)
    return format_percent(offset_total / adjusted_begin)
