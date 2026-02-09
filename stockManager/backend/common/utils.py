"""公共工具函数模块"""
from typing import Dict, List, Any
from ..models import Operation
import copy


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


def remove_operation_list_from_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """从计算结果中移除 operationList (用于缓存)"""
    result_copy = copy.deepcopy(result)
    for stock in result_copy.get("stocks", []):
        stock.pop("operationList", None)
    return result_copy


def merge_operation_list_to_result(cached_result: Dict[str, Any], operation_list: Dict[str, List[Operation]]) -> Dict[str, Any]:
    """将 operationList 合并到缓存的计算结果中"""
    result = copy.deepcopy(cached_result)
    for stock in result.get("stocks", []):
        code = stock.get("code")
        if code and code in operation_list:
            stock["operationList"] = [op.to_dict() for op in reversed(operation_list[code])]
    return result
