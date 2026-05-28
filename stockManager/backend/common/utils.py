"""公共工具函数模块"""
from collections import defaultdict

from ..models import Operation


def operation_sort_key(op: Operation) -> tuple:
    """Operation 统一排序键：(date, sortOrder, id)"""
    return (op.date, op.sortOrder, op.id)


def format_percent(value: float, precision: int = 2) -> str:
    """格式化浮点数为百分比字符串"""
    return f"{value * 100:.{precision}f}%"


def format_operations(operation_list: list[Operation]) -> dict[str, list[Operation]]:
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
