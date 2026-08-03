"""组合基金份额法日净值回放（纯计算，不含 incomeCash / 无 I/O）"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import NamedTuple

from backend.common import logger
from backend.common.domain.market import is_hk_code
from backend.common.domain.operations import apply_operation_to_hold, operation_cash_delta_cny
from backend.common.types import (
    CashFlowList,
    DailyCloseByCode,
    DateRangeList,
    HoldingWindows,
    OperationDict,
)
from backend.common.utils import operation_sort_key
from backend.models import Operation
from backend.services.calculation.constants import (
    MIN_HOLD_COUNT_THRESHOLD,
    MIN_VALUE_THRESHOLD,
)
from backend.services.calculation.holdings.stock_hold import StockHold

_MIN_UNITS = 1e-8


class NavDayRow(NamedTuple):
    date: date
    nav: float
    units: float
    asset: float
    cash: float


def _parse_flow_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(value, '%Y-%m-%d').date()


def resolve_start_date(
    operations: list[Operation],
    cash_flows: CashFlowList,
) -> date | None:
    dates: list[date] = []
    if operations:
        dates.append(min(op.date for op in operations))
    for flow in cash_flows:
        if flow.get('amount'):
            dates.append(_parse_flow_date(flow['date']))
    return min(dates) if dates else None


def _apply_cash_flow(
    amount: float,
    *,
    nav: float,
    units: float,
    cash: float,
) -> tuple[float, float, float]:
    """按当前净值申购/赎回；首笔入金时 nav 视为 1。"""
    if abs(amount) < MIN_VALUE_THRESHOLD:
        return nav, units, cash

    if amount > 0:
        price = nav if units > _MIN_UNITS else 1.0
        if price <= 0:
            price = 1.0
        units += amount / price
        cash += amount
        if units > _MIN_UNITS and nav <= 0:
            nav = 1.0
        return nav, units, cash

    withdraw = abs(amount)
    price = nav if nav > 0 else 1.0
    if units > _MIN_UNITS:
        redeem = min(withdraw / price, units)
        units -= redeem
    cash -= withdraw
    return nav, units, cash


def _apply_operation_cash_and_hold(
    holdings: dict[str, float],
    cash: float,
    operation: Operation,
) -> float:
    code = operation.code
    hold = holdings.get(code, 0.0)
    cash += operation_cash_delta_cny(operation, hold)
    holdings[code] = apply_operation_to_hold(hold, operation)
    if abs(holdings.get(code, 0.0)) < MIN_HOLD_COUNT_THRESHOLD:
        holdings.pop(code, None)
    return cash


def _mark_to_market(
    holdings: dict[str, float],
    prices: DailyCloseByCode,
    last_closes: dict[str, float],
    day: date,
    hkd_cny_rate: float,
    missing_logged: set[str] | None = None,
) -> float:
    mv = 0.0
    for code, hold in holdings.items():
        if abs(hold) < MIN_HOLD_COUNT_THRESHOLD:
            continue
        if (px := prices.get(code, {}).get(day)) is None or px <= 0:
            px = last_closes.get(code)
        if px is None or px <= 0:
            if missing_logged is not None and code not in missing_logged:
                missing_logged.add(code)
                logger.warning(
                    f"[nav] 持仓 {code} 无可用收盘价（首次见于 {day}），市值按 0"
                )
            continue
        last_closes[code] = px
        fx = hkd_cny_rate if is_hk_code(code) else 1.0
        mv += hold * px * fx
    return mv


def _align_events_to_sessions(
    events_by_date: dict[date, list],
    sessions: list[date],
) -> dict[date, list]:
    """将非交易日事件并入下一交易日（含当日）。"""
    if not sessions:
        return {}
    aligned: dict[date, list] = defaultdict(list)
    for d, items in events_by_date.items():
        target: date | None = None
        for s in sessions:
            if s >= d:
                target = s
                break
        if target is None:
            continue
        aligned[target].extend(items)
    return aligned


def _compute_nav_series(
    *,
    sessions: list[date],
    operations_by_date: dict[date, list[Operation]],
    flows_by_date: dict[date, list[float]],
    prices: DailyCloseByCode,
    hkd_cny_rate: float,
    start_nav: float = 1.0,
    start_units: float = 0.0,
    start_cash: float = 0.0,
    start_holdings: dict[str, float] | None = None,
) -> list[NavDayRow]:
    """对给定交易日序列回放净值。"""
    nav = start_nav if start_nav > 0 else 1.0
    units = start_units
    cash = start_cash
    holdings: dict[str, float] = dict(start_holdings or {})
    last_closes: dict[str, float] = {}
    missing_logged: set[str] = set()
    for code, series in prices.items():
        if series:
            before = [d for d in series if sessions and d < sessions[0]]
            if before:
                last_closes[code] = series[max(before)]
            elif sessions and sessions[0] in series:
                last_closes[code] = series[sessions[0]]

    rows: list[NavDayRow] = []
    for day in sessions:
        for amount in flows_by_date.get(day, []):
            nav, units, cash = _apply_cash_flow(
                amount, nav=nav, units=units, cash=cash
            )

        for operation in operations_by_date.get(day, []):
            cash = _apply_operation_cash_and_hold(holdings, cash, operation)

        mv = _mark_to_market(
            holdings, prices, last_closes, day, hkd_cny_rate, missing_logged
        )
        asset = cash + mv

        if units > _MIN_UNITS:
            nav = asset / units
        elif asset > MIN_VALUE_THRESHOLD:
            units = asset
            nav = 1.0
        else:
            nav = nav if nav > 0 else 1.0

        rows.append(NavDayRow(date=day, nav=nav, units=units, asset=asset, cash=cash))

    return rows


def group_operations(operation_list: OperationDict) -> tuple[list[Operation], dict[date, list[Operation]]]:
    all_ops: list[Operation] = []
    by_date: dict[date, list[Operation]] = defaultdict(list)
    for ops in operation_list.values():
        for op in ops:
            all_ops.append(op)
            by_date[op.date].append(op)
    for day in by_date:
        by_date[day].sort(key=operation_sort_key)
    return all_ops, by_date


def group_cash_flows(cash_flow_list: CashFlowList) -> dict[date, list[float]]:
    by_date: dict[date, list[float]] = defaultdict(list)
    for flow in cash_flow_list:
        amount = float(flow.get('amount') or 0)
        if abs(amount) < MIN_VALUE_THRESHOLD:
            continue
        by_date[_parse_flow_date(flow['date'])].append(amount)
    return by_date


def holdings_at(operation_list: OperationDict, target: date) -> dict[str, float]:
    holdings: dict[str, float] = {}
    for code, ops in operation_list.items():
        sorted_ops = sorted(ops, key=operation_sort_key)
        hold = StockHold.calculate_hold_count_at_date(sorted_ops, target)
        if abs(hold) >= MIN_HOLD_COUNT_THRESHOLD:
            holdings[code] = hold
    return holdings


def holding_windows(
    operation_list: OperationDict,
    end: date,
) -> HoldingWindows:
    """按交易回放得到每只股票的持仓区间 [start, end]（可多段）。"""
    result: HoldingWindows = {}
    for code, ops in operation_list.items():
        sorted_ops = sorted(ops, key=operation_sort_key)
        if not sorted_ops:
            continue
        hold = 0.0
        window_start: date | None = None
        windows: DateRangeList = []
        for operation in sorted_ops:
            if operation.date > end:
                break
            prev = hold
            hold = apply_operation_to_hold(hold, operation)
            opened = (
                abs(prev) < MIN_HOLD_COUNT_THRESHOLD
                and abs(hold) >= MIN_HOLD_COUNT_THRESHOLD
            )
            closed = (
                abs(prev) >= MIN_HOLD_COUNT_THRESHOLD
                and abs(hold) < MIN_HOLD_COUNT_THRESHOLD
            )
            if opened:
                window_start = operation.date
            if closed and window_start is not None:
                windows.append((window_start, operation.date))
                window_start = None
        if window_start is not None and abs(hold) >= MIN_HOLD_COUNT_THRESHOLD:
            windows.append((window_start, end))
        if windows:
            result[code] = windows
    return result


def clip_windows_to_range(
    windows: HoldingWindows,
    range_start: date,
    end: date,
    *,
    seed_date: date | None = None,
) -> HoldingWindows:
    """截取与 [range_start, end] 有交集的窗口；增量时用 seed_date 预取昨收。"""
    clipped: HoldingWindows = {}
    for code, wins in windows.items():
        out: DateRangeList = []
        for start, stop in wins:
            cs = max(start, range_start)
            ce = min(stop, end)
            if seed_date is not None and start <= seed_date <= stop:
                cs = min(cs, seed_date)
            if cs <= ce:
                out.append((cs, ce))
        if out:
            clipped[code] = out
    return clipped


def compute_nav_rows(
    *,
    operation_list: OperationDict,
    cash_flow_list: CashFlowList,
    sessions: list[date],
    prices: DailyCloseByCode,
    hkd_cny_rate: float,
    event_cutoff: date | None = None,
    start_nav: float = 1.0,
    start_units: float = 0.0,
    start_cash: float = 0.0,
    start_holdings: dict[str, float] | None = None,
) -> list[NavDayRow]:
    """给定交易日与收盘价，回放净值序列（无 I/O）。"""
    _all_ops, ops_by_date = group_operations(operation_list)
    flows_by_date = group_cash_flows(cash_flow_list)

    if event_cutoff is not None:
        filtered_ops = {d: v for d, v in ops_by_date.items() if d > event_cutoff}
        filtered_flows = {d: v for d, v in flows_by_date.items() if d > event_cutoff}
    else:
        filtered_ops = ops_by_date
        filtered_flows = flows_by_date

    return _compute_nav_series(
        sessions=sessions,
        operations_by_date=_align_events_to_sessions(filtered_ops, sessions),
        flows_by_date=_align_events_to_sessions(filtered_flows, sessions),
        prices=prices,
        hkd_cny_rate=hkd_cny_rate,
        start_nav=start_nav,
        start_units=start_units,
        start_cash=start_cash,
        start_holdings=start_holdings,
    )
