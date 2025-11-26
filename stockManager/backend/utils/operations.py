"""操作记录相关工具函数模块"""
from typing import Dict, List
from ..models import Operation


def format_operations(operation_list: List[Operation]) -> Dict[str, List[Operation]]:
    """按股票代码分组操作记录"""
    result = {}
    for operation in operation_list:
        if operation.code not in result:
            result[operation.code] = []
        result[operation.code].append(operation)
    return result


def _safe_float(value: str, default: float = 0.0) -> float:  # noqa: F401
    """安全地将字符串转换为浮点数"""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default

