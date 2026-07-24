"""单股操作账本：一次遍历计算持股、成本、摊薄等指标（双账本）。"""
import datetime
from dataclasses import dataclass

from backend.common.constants import OperationType
from backend.common.operations import apply_operation_to_hold, dividend_multiplier
from backend.common.settlement import (
    buy_cost_native,
    buy_outflow_cny,
    dividend_cash_cny,
    dividend_cash_native,
    sell_inflow_cny,
    sell_proceeds_native,
    trade_fee_cny,
)
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
    current_overall_native: float
    current_overall_cny: float
    hold_cost_basis_cny: float
    today_input_native: float
    today_input_cny: float
    total_fee_cny: float
    holding_duration: int

    def overall_cost_per_share(self) -> float:
        """累计投入(原币) / 当前持股；不持有时返回 0.0。"""
        if abs(self.current_hold_count) < MIN_HOLD_COUNT_THRESHOLD:
            return 0.0
        return self.current_overall_native / self.current_hold_count

    def offset_current_cny(self, market_value_cny: float) -> float:
        """人民币浮动盈亏：市值(CNY) - 当前持仓成本基数(CNY)。"""
        return market_value_cny - self.hold_cost_basis_cny

    def offset_current_ratio(self, price_now: float) -> float:
        """浮动盈亏率：(现价 - 持仓成本) / 持仓成本（原币口径）。"""
        if abs(self.current_hold_cost) < MIN_PRICE_THRESHOLD:
            return 0.0
        return (price_now - self.current_hold_cost) / self.current_hold_cost

    def offset_total_cny(self, market_value_cny: float) -> float:
        """人民币累计盈亏：市值(CNY) - 累计投入净额(CNY)。"""
        return market_value_cny - self.current_overall_cny

    def offset_today_cny(
        self,
        market_value_cny: float,
        yesterday_value_cny: float,
    ) -> float:
        """人民币今日总盈亏。"""
        if yesterday_value_cny < MIN_VALUE_THRESHOLD:
            return self.offset_current_cny(market_value_cny)
        return market_value_cny - yesterday_value_cny - self.today_input_cny


def compute_single_metrics(
    operations: list[Operation],
    hkd_cny_rate: float = 0.86,
) -> SingleStockMetrics:
    """一次遍历计算所有单股账本指标（原币展示账本 + 人民币资金账本）。"""
    today = datetime.date.today()

    current_hold = 0.0
    yesterday_hold = 0.0

    hold_total_pay_native = 0.0
    hold_total_pay_cny = 0.0
    hold_total_count = 0.0

    overall_sum_native = 0.0
    overall_sum_cny = 0.0

    today_input_native = 0.0
    today_input_cny = 0.0
    total_fee_cny = 0.0

    holding_start_date = None
    total_holding_days = 0

    for operation in operations:
        op_type = operation.operationType

        total_fee_cny += trade_fee_cny(operation)

        is_today = operation.date == today

        if op_type == OperationType.BUY:
            previous_hold = current_hold
            current_hold += operation.count

            cost_native = buy_cost_native(operation)
            cost_cny = buy_outflow_cny(operation)

            hold_total_pay_native += cost_native
            hold_total_pay_cny += cost_cny
            hold_total_count += operation.count

            overall_sum_native += cost_native
            overall_sum_cny += cost_cny

            if is_today:
                today_input_native += cost_native
                today_input_cny += cost_cny

            if previous_hold < 1 and current_hold >= 1:
                holding_start_date = operation.date

        elif op_type == OperationType.SELL:
            previous_hold = current_hold
            current_hold -= operation.count

            proceeds_native = sell_proceeds_native(operation)
            inflow_cny = sell_inflow_cny(operation)

            overall_sum_native -= proceeds_native
            overall_sum_cny -= inflow_cny

            if is_today:
                today_input_native -= proceeds_native
                today_input_cny -= inflow_cny

            if previous_hold >= 1 and current_hold < 1:
                if holding_start_date:
                    duration = (operation.date - holding_start_date).days
                    total_holding_days += duration
                    holding_start_date = None

            if current_hold == 0:
                hold_total_pay_native = 0.0
                hold_total_pay_cny = 0.0
                hold_total_count = 0.0

        elif op_type == OperationType.DIVIDEND:
            multiplier = dividend_multiplier(operation)
            hold_total_count += hold_total_count * multiplier
            overall_sum_native -= dividend_cash_native(
                operation, current_hold, hkd_cny_rate
            )
            overall_sum_cny -= dividend_cash_cny(operation, current_hold)
            current_hold = apply_operation_to_hold(current_hold, operation)

        if not is_today:
            yesterday_hold = current_hold

    if current_hold >= 1 and holding_start_date:
        duration = (today - holding_start_date).days
        total_holding_days += duration

    current_hold_cost = (
        hold_total_pay_native / hold_total_count
        if abs(hold_total_count) >= MIN_HOLD_COUNT_THRESHOLD
        else 0.0
    )

    return SingleStockMetrics(
        current_hold_count=current_hold,
        yesterday_hold_count=yesterday_hold,
        current_hold_cost=current_hold_cost,
        current_overall_native=overall_sum_native,
        current_overall_cny=overall_sum_cny,
        hold_cost_basis_cny=hold_total_pay_cny,
        today_input_native=today_input_native,
        today_input_cny=today_input_cny,
        total_fee_cny=total_fee_cny,
        holding_duration=total_holding_days,
    )
