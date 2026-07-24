"""资金加权累计收益率计算（人民币资金账本口径）。"""
import datetime

from backend.common.constants import OperationType
from backend.common.operations import apply_net_invested
from backend.common.settlement import buy_outflow_cny
from backend.common.utils import operation_sort_key
from backend.models import Operation
from backend.services.calculation.constants import MIN_HOLD_COUNT_THRESHOLD, MIN_VALUE_THRESHOLD


def calculate_money_weighted_return(
    operations: list[Operation],
    offset_total: float,
) -> float:
    """资金加权累计收益率：offsetTotal(CNY) / 加权平均占用资金(CNY)。"""
    sorted_ops = sorted(operations, key=operation_sort_key)
    if not sorted_ops:
        return 0.0

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

        net_invested, current_hold = apply_net_invested(
            net_invested, current_hold, operation
        )
        peak_net_invested = max(peak_net_invested, max(net_invested, 0.0))
        if operation.operationType == OperationType.BUY:
            total_buy_amount += buy_outflow_cny(operation)
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
        return 0.0
    return offset_total / adjusted_begin
