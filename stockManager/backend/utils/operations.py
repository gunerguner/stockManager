"""
操作记录相关工具函数模块
提供操作记录处理等功能
"""
from typing import Dict, List
from ..models import Operation


def format_operations(operation_list: List[Operation]) -> Dict[str, List[Operation]]:
    """
    格式化操作记录列表,按股票代码分组
    
    Args:
        operation_list: 操作记录列表
        
    Returns:
        Dict[str, List[Operation]]: 股票代码到操作记录列表的映射
    """
    result = {}
    for operation in operation_list:
        if operation.code not in result:
            result[operation.code] = []
        result[operation.code].append(operation)
    
    return result


def _safe_float(value: str, default: float = 0.0) -> float:
    """安全地将字符串转换为浮点数"""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default

