"""资金加权累计收益率计算（人民币资金账本口径）。"""
import datetime

from backend.common.constants import OperationType
from backend.common.domain.operations import apply_net_invested
from backend.common.domain.settlement import buy_outflow_cny
from backend.common.utils import operation_sort_key
from backend.models import Operation
from backend.common.thresholds import MIN_MONEY, MIN_QTY


def calculate_money_weighted_return(
    operations: list[Operation],
    offset_total: float,
) -> float:
    """资金加权累计收益率：offsetTotal(CNY) / 加权平均占用资金(CNY)。"""
    if not (sorted_ops := sorted(operations, key=operation_sort_key)):
        return 0.0

    net_invested = current_hold = dollar_days = holding_days = 0.0
    peak_net_invested = total_buy_amount = 0.0
    seg_start = sorted_ops[0].date

    for operation in sorted_ops:
        if (
            (seg_days := (operation.date - seg_start).days) > 0
            and current_hold >= MIN_QTY
        ):
            dollar_days += max(net_invested, 0.0) * seg_days
            holding_days += seg_days

        net_invested, current_hold = apply_net_invested(
            net_invested, current_hold, operation
        )
        peak_net_invested = max(peak_net_invested, net_invested, 0.0)
        if operation.operationType == OperationType.BUY:
            total_buy_amount += buy_outflow_cny(operation)
        seg_start = operation.date

    # 仍持仓则补到今天；已清仓尾段为 0，不必再算
    if (
        current_hold >= MIN_QTY
        and (tail_days := (datetime.date.today() - seg_start).days) > 0
    ):
        dollar_days += max(net_invested, 0.0) * tail_days
        holding_days += tail_days

    if holding_days >= MIN_MONEY:
        adjusted_begin = dollar_days / holding_days
    else:
        adjusted_begin = (
            peak_net_invested
            if peak_net_invested >= MIN_MONEY
            else total_buy_amount
        )

    return offset_total / adjusted_begin if adjusted_begin >= MIN_MONEY else 0.0
