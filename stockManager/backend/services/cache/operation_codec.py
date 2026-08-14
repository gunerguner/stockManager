"""Operation 缓存序列化/反序列化"""
import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from django.contrib.auth.models import User
from django.db.models.base import ModelState

from backend.models import Operation
from backend.common.types import OperationDict

_OPERATION_FIELDS = (
    "id",
    "sortOrder",
    "operationType",
    "price",
    "count",
    "fee",
    "amount",
    "comment",
    "cash",
    "stock",
    "reserve",
)

_DECIMAL_FIELDS = frozenset({"price", "fee", "amount", "cash"})


def _serialize_value(field: str, value: Any) -> Any:
    """Decimal 存字符串，避免 json.dumps 失败；amount 可为空。"""
    if field in _DECIMAL_FIELDS:
        if value is None:
            return None
        return str(value)
    return value


def _deserialize_value(field: str, value: Any) -> Any:
    if field not in _DECIMAL_FIELDS:
        return value
    if value is None:
        return None
    return Decimal(str(value))


def _serialize_operation(op: Operation) -> dict:
    data = {
        field: _serialize_value(field, getattr(op, field))
        for field in _OPERATION_FIELDS
    }
    data["date"] = str(op.date)
    return data


def serialize_operations(operations: OperationDict) -> str:
    return json.dumps({
        code: [_serialize_operation(op) for op in op_list]
        for code, op_list in operations.items()
    })


def operation_from_cache(code: str, op_data: dict, user_id: int) -> Operation:
    op = Operation.__new__(Operation)

    state = ModelState()
    state.adding = False
    state.db = "default"

    op._state = state
    setattr(op, "user_id", user_id)
    op.code = code
    op.date = datetime.strptime(op_data["date"], "%Y-%m-%d").date()
    for field in _OPERATION_FIELDS:
        if field == "sortOrder":
            setattr(op, field, op_data.get(field, 0))
        elif field == "amount":
            setattr(op, field, _deserialize_value(field, op_data.get(field)))
        else:
            setattr(op, field, _deserialize_value(field, op_data[field]))
    return op


def deserialize_operations(data: str, user: User) -> OperationDict:
    operations_dict = json.loads(data)
    user_id = int(user.pk)
    return {
        code: [operation_from_cache(code, op_data, user_id) for op_data in op_list]
        for code, op_list in operations_dict.items()
    }
