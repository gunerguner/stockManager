"""公共工具函数模块"""
from collections import defaultdict
from collections.abc import Iterable

from backend.common.types import RealtimePriceData
from backend.models import Operation


def extract_offset_today(
    price_now: float | None,
    price_data: RealtimePriceData | dict | None = None,
) -> tuple[float, float]:
    """从现价与行情数据提取当日涨跌额与比率。"""
    if price_now is None or price_now < 0.001:
        return 0.0, 0.0
    data = price_data or {}
    return data.get("priceOffset", 0.0), data.get("offsetRatio", 0.0)


def operation_sort_key(op: Operation) -> tuple:
    """Operation 统一排序键：(date, sortOrder, id)"""
    return (op.date, op.sortOrder, op.pk)


def format_operations(operation_list: Iterable[Operation]) -> dict[str, list[Operation]]:
    """按股票代码分组操作记录"""
    grouped: defaultdict[str, list[Operation]] = defaultdict(list)
    for operation in operation_list:
        grouped[operation.code].append(operation)
    return dict(grouped)


def safe_float(value: str, default: float = 0.0) -> float:
    """安全地将字符串转换为浮点数"""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default
