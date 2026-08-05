"""净值回放事件：日期解析、分组、非交易日对齐（纯计算）"""
from bisect import bisect_left
from collections import defaultdict
from datetime import date, datetime

from backend.common.types import CashFlowList, OperationDict
from backend.common.utils import operation_sort_key
from backend.models import Operation
from backend.common.thresholds import MIN_MONEY


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


def _align_events_to_sessions(
    events_by_date: dict[date, list],
    sessions: list[date],
) -> dict[date, list]:
    """将非交易日事件并入下一交易日（含当日）。"""
    if not sessions:
        return {}
    aligned: dict[date, list] = defaultdict(list)
    for d, items in events_by_date.items():
        idx = bisect_left(sessions, d)
        if idx >= len(sessions):
            continue
        aligned[sessions[idx]].extend(items)
    return aligned


def group_operations(
    operation_list: OperationDict,
) -> tuple[list[Operation], dict[date, list[Operation]]]:
    all_ops = [op for ops in operation_list.values() for op in ops]
    by_date: dict[date, list[Operation]] = defaultdict(list)
    for op in all_ops:
        by_date[op.date].append(op)
    for day in by_date:
        by_date[day].sort(key=operation_sort_key)
    return all_ops, by_date


def group_cash_flows(cash_flow_list: CashFlowList) -> dict[date, list[float]]:
    by_date: dict[date, list[float]] = defaultdict(list)
    for flow in cash_flow_list:
        amount = float(flow.get('amount') or 0)
        if abs(amount) < MIN_MONEY:
            continue
        by_date[_parse_flow_date(flow['date'])].append(amount)
    return by_date
