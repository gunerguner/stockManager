"""公共工具函数模块"""
from collections import defaultdict
from collections.abc import Iterable
from enum import Enum

from backend.common.thresholds import MIN_QTY
from backend.common.types import CashFlowList, OperationData, RealtimePriceData
from backend.models import Operation


def extract_offset_today(
    price_now: float | None,
    price_data: RealtimePriceData | dict | None = None,
) -> tuple[float, float]:
    """从现价与行情数据提取当日涨跌额与比率。"""
    if price_now is None or price_now < MIN_QTY:
        return 0.0, 0.0
    data = price_data or {}
    return data.get("priceOffset", 0.0), data.get("offsetRatio", 0.0)


def safe_ratio(
    numerator: float | None,
    denominator: float | None,
    digits: int = 2,
) -> float | None:
    """两数相除并四舍五入；任一方缺失或为 0 时返回 None（如 PE/PB）。"""
    if numerator and denominator:
        return round(numerator / denominator, digits)
    return None


def sum_origin_cash(cash_flow_list: CashFlowList) -> float:
    """出入金合计（本金口径）。"""
    return sum(float(flow.get("amount") or 0) for flow in cash_flow_list)


def operation_to_api(op: Operation) -> OperationData:
    """API 边界：Decimal 转 float，避免 JsonResponse 把金额编成字符串。"""
    raw_type = op.operationType
    op_type = raw_type.value if isinstance(raw_type, Enum) else str(raw_type)
    amount = op.amount
    return {
        "date": str(op.date),
        "type": op_type,
        "price": float(op.price),
        "count": op.count,
        "fee": float(op.fee),
        "amount": float(amount) if amount is not None else None,
        "comment": op.comment,
        "cash": float(op.cash),
        "stock": op.stock,
        "reserve": op.reserve,
    }


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
