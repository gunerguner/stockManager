"""交易日缺口识别与窗口合并（日频价格 / 汇率共用）"""
from datetime import date

from backend.common.domain.calendar import TradingCalendar
from backend.common.domain.market import Market
from backend.common.types import DateRangeList


def merge_windows(windows: DateRangeList) -> DateRangeList:
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


def missing_session_gaps(
    have: dict[date, float],
    start: date,
    end: date,
    market: Market = Market.CN,
) -> DateRangeList:
    """在 [start, end] 的对应市场交易日中，找出缺失有效值的连续区间。"""
    if start > end or not (
        sessions := TradingCalendar.sessions_between(start, end, market)
    ):
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
