"""日频收盘价持久化与缺口补拉（按持仓窗口 + 交易日差集 + 并发）"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

from django.db import close_old_connections, transaction

from backend.common import logger
from backend.common.market import Market, code_to_market
from backend.common.tradingCalendar import TradingCalendar
from backend.common.types import (
    DailyCloseByCode,
    DailyCloseSeries,
    DateRangeList,
    HoldingWindows,
)
from backend.models import StockDailyPrice
from backend.services.market.historicalDaily import fetch_daily_closes

_MAX_WORKERS = 6
_GAP_FILL_ROUNDS = 2


def load_closes(
    codes: list[str],
    start: date,
    end: date,
) -> DailyCloseByCode:
    """从 DB 读取 [start, end] 内已有收盘价。"""
    if not codes or start > end:
        return {code: {} for code in codes}
    rows = StockDailyPrice.objects.filter(
        code__in=codes,
        date__gte=start,
        date__lte=end,
    ).values_list('code', 'date', 'close')
    result: DailyCloseByCode = {code: {} for code in codes}
    for code, d, close in rows:
        result.setdefault(code, {})[d] = float(close)
    return result


def _merge_windows(windows: DateRangeList) -> DateRangeList:
    if not windows:
        return []
    ordered = sorted(windows, key=lambda w: (w[0], w[1]))
    merged: DateRangeList = [ordered[0]]
    for start, end in ordered[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end or (start - prev_end).days <= 1:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def _missing_session_gaps(
    have: DailyCloseSeries,
    start: date,
    end: date,
    market: Market = Market.CN,
) -> DateRangeList:
    """在 [start, end] 的对应市场交易日中，找出缺失收盘价的连续区间。"""
    if start > end:
        return []
    sessions = TradingCalendar.sessions_between(start, end, market)
    if not sessions:
        return []
    gaps: DateRangeList = []
    gap_start: date | None = None
    gap_end: date | None = None
    for d in sessions:
        if d in have and have[d] > 0:
            if gap_start is not None and gap_end is not None:
                gaps.append((gap_start, gap_end))
            gap_start = None
            gap_end = None
        else:
            if gap_start is None:
                gap_start = d
            gap_end = d
    if gap_start is not None and gap_end is not None:
        gaps.append((gap_start, gap_end))
    return gaps


def _fetch_and_upsert_gaps(code: str, gaps: DateRangeList) -> DailyCloseSeries:
    fetched_all: DailyCloseSeries = {}
    for gap_start, gap_end in gaps:
        fetched = fetch_daily_closes(code, gap_start, gap_end)
        if not fetched:
            logger.warning(f"[daily_price] {code} 缺口 {gap_start}~{gap_end} 为空")
            continue
        fetched_all.update(fetched)
    if fetched_all:
        close_old_connections()
        _upsert_prices(code, fetched_all)
    return fetched_all


def _gaps_in_windows(
    existing: DailyCloseSeries,
    windows: DateRangeList,
    market: Market,
) -> DateRangeList:
    gaps: DateRangeList = []
    for start, end in windows:
        gaps.extend(_missing_session_gaps(existing, start, end, market))
    return _merge_windows(gaps)


def _ensure_one_code_windows(
    code: str,
    windows: DateRangeList,
) -> DailyCloseSeries:
    close_old_connections()
    market = code_to_market(code)
    merged = _merge_windows([(s, e) for s, e in windows if s <= e])
    if not merged:
        return {}
    overall_start = merged[0][0]
    overall_end = max(e for _, e in merged)
    existing = load_closes([code], overall_start, overall_end).get(code) or {}

    for round_idx in range(_GAP_FILL_ROUNDS):
        gaps = _gaps_in_windows(existing, merged, market)
        if not gaps:
            break
        logger.info(
            f"[daily_price] {code} 第 {round_idx + 1} 轮补拉 {len(gaps)} 个缺口: "
            + ", ".join(f"{a}~{b}" for a, b in gaps[:8])
            + (" ..." if len(gaps) > 8 else "")
        )
        existing.update(_fetch_and_upsert_gaps(code, gaps))
    else:
        remain = _gaps_in_windows(existing, merged, market)
        if remain:
            miss_days = sum(
                len(TradingCalendar.sessions_between(a, b, market))
                for a, b in remain
            )
            logger.warning(
                f"[daily_price] {code} 仍缺约 {miss_days} 个交易日 "
                f"({remain[0][0]}~{remain[-1][1]})"
            )

    return existing


def ensure_daily_prices_for_windows(windows: HoldingWindows) -> DailyCloseByCode:
    """按持仓窗口确保日 K：只补交易日缺口，多股票并发拉取。"""
    cleaned: HoldingWindows = {
        code: [(s, e) for s, e in wins if s <= e]
        for code, wins in windows.items()
        if wins
    }
    cleaned = {code: wins for code, wins in cleaned.items() if wins}
    if not cleaned:
        return {}

    result: DailyCloseByCode = {}
    codes = list(cleaned.keys())
    workers = min(_MAX_WORKERS, len(codes))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(_ensure_one_code_windows, code, wins): code
            for code, wins in cleaned.items()
        }
        for future in as_completed(futures):
            code = futures[future]
            try:
                result[code] = future.result()
            except Exception as e:
                logger.error(f"[daily_price] {code} 补拉失败: {e}", exc_info=True)
                result[code] = {}

    close_old_connections()
    return result


def _upsert_prices(code: str, closes: DailyCloseSeries) -> None:
    if not closes:
        return
    objs = [
        StockDailyPrice(code=code, date=d, close=px)
        for d, px in closes.items()
    ]
    with transaction.atomic():
        StockDailyPrice.objects.bulk_create(
            objs,
            update_conflicts=True,
            unique_fields=['code', 'date'],
            update_fields=['close'],
        )
