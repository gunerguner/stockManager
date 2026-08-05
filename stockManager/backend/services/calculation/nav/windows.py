"""净值取价持仓窗口（纯计算）"""
from datetime import date

from backend.common.domain.operations import apply_operation_to_hold
from backend.common.types import DateRangeList, HoldingWindows, OperationDict
from backend.common.utils import operation_sort_key
from backend.models import Operation
from backend.common.thresholds import MIN_QTY
from backend.services.calculation.holdings.stock_hold import StockHold


def holdings_at(operation_list: OperationDict, target: date) -> dict[str, float]:
    return {
        code: hold
        for code, ops in operation_list.items()
        if abs(
            hold := StockHold.calculate_hold_count_at_date(sorted(ops, key=operation_sort_key), target)
        ) >= MIN_QTY
    }


def _windows_for_ops(ops: list[Operation], end: date) -> DateRangeList:
    if not (sorted_ops := sorted(ops, key=operation_sort_key)):
        return []
    hold = 0.0
    window_start: date | None = None
    windows: DateRangeList = []
    thr = MIN_QTY
    for operation in sorted_ops:
        if operation.date > end:
            break
        prev, hold = hold, apply_operation_to_hold(hold, operation)
        was_held, now_held = abs(prev) >= thr, abs(hold) >= thr
        if not was_held and now_held:
            window_start = operation.date
        elif was_held and not now_held and window_start is not None:
            windows.append((window_start, operation.date))
            window_start = None
    if window_start is not None and abs(hold) >= thr:
        windows.append((window_start, end))
    return windows


def holding_windows(operation_list: OperationDict, end: date) -> HoldingWindows:
    """按交易回放得到每只股票的持仓区间 [start, end]（可多段）。"""
    return {
        code: wins
        for code, ops in operation_list.items()
        if (wins := _windows_for_ops(ops, end))
    }


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
