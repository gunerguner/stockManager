"""公共工具函数模块"""
from typing import Dict, List
from ..models import Operation


def format_percent(value: float, precision: int = 2) -> str:
    """格式化浮点数为百分比字符串"""
    return f"{value * 100:.{precision}f}%"


def format_operations(operation_list: List[Operation]) -> Dict[str, List[Operation]]:
    """按股票代码分组操作记录"""
    result = {}
    for operation in operation_list:
        if operation.code not in result:
            result[operation.code] = []
        result[operation.code].append(operation)
    return result


def safe_float(value: str, default: float = 0.0) -> float:
    """安全地将字符串转换为浮点数"""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default
