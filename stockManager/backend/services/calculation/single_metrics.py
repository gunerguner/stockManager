"""单股操作账本：一次遍历计算持股、成本、摊薄等指标"""
import datetime
from dataclasses import dataclass

from backend.common.constants import OperationType
from backend.common.operations import apply_operation_to_hold, dividend_multiplier
from backend.models import Operation
from backend.services.calculation.constants import (
    MIN_HOLD_COUNT_THRESHOLD,
    MIN_PRICE_THRESHOLD,
    MIN_VALUE_THRESHOLD,
)


@dataclass(frozen=True)
class SingleStockMetrics:
    current_hold_count: float
    yesterday_hold_count: float
    current_hold_cost: float
    current_overall: float
    today_input: float
    total_fee: float
    holding_duration: int

    def is_holding(self) -> bool:
        """当前是否仍持有该股（持仓数绝对值超过最小阈值）。"""
        return abs(self.current_hold_count) >= MIN_HOLD_COUNT_THRESHOLD

    def overall_cost_per_share(self) -> float:
        """累计投入 / 当前持股；不持有时返回 0.0。"""
        if not self.is_holding():
            return 0.0
        return self.current_overall / self.current_hold_count

    def offset_current(self, price_now: float) -> float:
        """给定最新价，返回浮动盈亏：(现价 - 持仓成本) × 持仓。"""
        return (price_now - self.current_hold_cost) * self.current_hold_count

    def offset_current_ratio(self, price_now: float) -> float:
        """给定最新价，返回浮动盈亏率：(现价 - 持仓成本) / 持仓成本。"""
        if abs(self.current_hold_cost) < MIN_PRICE_THRESHOLD:
            return 0.0
        return (price_now - self.current_hold_cost) / self.current_hold_cost

    def offset_total(self, price_now: float) -> float:
        """给定最新价，返回累计盈亏：现价 × 持仓 - 累计投入净额。"""
        return price_now * self.current_hold_count - self.current_overall

    def offset_today(
        self,
        price_now: float,
        yesterday_close: float,
        total_value_yesterday: float,
    ) -> float:
        """给定今收、昨收、昨市值，返回今日总盈亏（含今日新增投入的扣减）。

        - 昨日市值过小（刚建仓等）时退化为 current_offset（不扣 today_input）。
        - 否则 = 现价 × 持仓 - 昨收 × 昨持仓 - 今日投入。
        """
        if total_value_yesterday < MIN_VALUE_THRESHOLD:
            return self.offset_current(price_now)
        return (
            price_now * self.current_hold_count
            - yesterday_close * self.yesterday_hold_count
            - self.today_input
        )


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
