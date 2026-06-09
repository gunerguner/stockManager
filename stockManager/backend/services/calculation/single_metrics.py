"""单股操作账本：一次遍历计算持股、成本、摊薄等指标"""
import datetime
from dataclasses import dataclass

from ...common.constants import OperationType
from ...common.operations import apply_operation_to_hold, dividend_multiplier
from ...models import Operation
from .constants import MIN_HOLD_COUNT_THRESHOLD


@dataclass(frozen=True)
class SingleStockMetrics:
    current_hold_count: float
    yesterday_hold_count: float
    current_hold_cost: float
    current_overall: float
    today_input: float
    total_fee: float
    holding_duration: int


def compute_single_metrics(operations: list[Operation]) -> SingleStockMetrics:
    """一次遍历计算所有单股账本指标"""
    today = datetime.date.today()

    current_hold = 0.0
    yesterday_hold = 0.0

    hold_total_pay = 0.0
    hold_total_count = 0.0

    overall_sum = 0.0

    today_input = 0.0
    total_fee = 0.0

    holding_start_date = None
    total_holding_days = 0

    for operation in operations:
        op_type = operation.operationType

        total_fee += operation.fee

        is_today = operation.date == today

        if op_type == OperationType.BUY:
            previous_hold = current_hold
            current_hold += operation.count

            hold_total_pay += operation.count * operation.price + operation.fee
            hold_total_count += operation.count

            overall_sum += operation.count * operation.price + operation.fee

            if is_today:
                today_input += operation.count * operation.price + operation.fee

            if previous_hold < 1 and current_hold >= 1:
                holding_start_date = operation.date

        elif op_type == OperationType.SELL:
            previous_hold = current_hold
            current_hold -= operation.count

            overall_sum -= operation.count * operation.price - operation.fee

            if is_today:
                today_input -= operation.count * operation.price + operation.fee

            if previous_hold >= 1 and current_hold < 1:
                if holding_start_date:
                    duration = (operation.date - holding_start_date).days
                    total_holding_days += duration
                    holding_start_date = None

            if current_hold == 0:
                hold_total_pay = 0.0
                hold_total_count = 0.0

        elif op_type == OperationType.DIVIDEND:
            multiplier = dividend_multiplier(operation)
            hold_total_count += hold_total_count * multiplier
            overall_sum -= current_hold * operation.cash
            current_hold = apply_operation_to_hold(current_hold, operation)

        if not is_today:
            yesterday_hold = current_hold

    if current_hold >= 1 and holding_start_date:
        duration = (today - holding_start_date).days
        total_holding_days += duration

    current_hold_cost = (
        hold_total_pay / hold_total_count
        if abs(hold_total_count) >= MIN_HOLD_COUNT_THRESHOLD
        else 0.0
    )

    return SingleStockMetrics(
        current_hold_count=current_hold,
        yesterday_hold_count=yesterday_hold,
        current_hold_cost=current_hold_cost,
        current_overall=overall_sum,
        today_input=today_input,
        total_fee=total_fee,
        holding_duration=total_holding_days,
    )
