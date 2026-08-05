"""组合基金份额法日净值序列回放（纯计算，不含 incomeCash / 无 I/O）"""
from datetime import date
from typing import NamedTuple

from backend.common import logger
from backend.common.domain.market import is_hk_code
from backend.common.domain.operations import apply_operation_to_hold, operation_cash_delta_cny
from backend.common.types import CashFlowList, DailyCloseByCode, OperationDict
from backend.models import Operation
from backend.common.thresholds import EPS, MIN_MONEY, MIN_QTY
from backend.services.calculation.nav.events import (
    _align_events_to_sessions,
    group_cash_flows,
    group_operations,
)


class NavDayRow(NamedTuple):
    date: date
    nav: float
    units: float
    asset: float
    cash: float


def _apply_cash_flow(
    amount: float,
    *,
    nav: float,
    units: float,
    cash: float,
) -> tuple[float, float, float]:
    """按当前净值申购/赎回；首笔入金时 nav 视为 1。"""
    if abs(amount) < MIN_MONEY:
        return nav, units, cash

    if amount > 0:
        price = nav if units > EPS else 1.0
        if price <= 0:
            price = 1.0
        units += amount / price
        cash += amount
        if units > EPS and nav <= 0:
            nav = 1.0
        return nav, units, cash

    withdraw = abs(amount)
    price = nav if nav > 0 else 1.0
    if units > EPS:
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
    if abs(new_hold := apply_operation_to_hold(hold, operation)) < MIN_QTY:
        holdings.pop(code, None)
    else:
        holdings[code] = new_hold
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
        if abs(hold) < MIN_QTY:
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
        if not series:
            continue
        if sessions and (before := [d for d in series if d < sessions[0]]):
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

        if units > EPS:
            nav = asset / units
        elif asset > MIN_MONEY:
            units = asset
            nav = 1.0
        else:
            nav = nav if nav > 0 else 1.0

        rows.append(NavDayRow(date=day, nav=nav, units=units, asset=asset, cash=cash))

    return rows


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

    def _after(by_date: dict) -> dict:
        return (
            {d: v for d, v in by_date.items() if d > event_cutoff}
            if event_cutoff is not None
            else by_date
        )

    return _compute_nav_series(
        sessions=sessions,
        operations_by_date=_align_events_to_sessions(_after(ops_by_date), sessions),
        flows_by_date=_align_events_to_sessions(_after(flows_by_date), sessions),
        prices=prices,
        hkd_cny_rate=hkd_cny_rate,
        start_nav=start_nav,
        start_units=start_units,
        start_cash=start_cash,
        start_holdings=start_holdings,
    )
