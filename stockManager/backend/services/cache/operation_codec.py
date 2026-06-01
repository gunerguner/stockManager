"""Operation 缓存序列化/反序列化"""
import json
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models.base import ModelState

from ...models import Operation
from ...common.types import OperationDict


def serialize_operations(operations: OperationDict) -> str:
    return json.dumps({
        code: [
            {
                'id': op.id,
                'date': str(op.date),
                'sortOrder': op.sortOrder,
                'operationType': op.operationType,
                'price': op.price,
                'count': op.count,
                'fee': op.fee,
                'comment': op.comment,
                'cash': op.cash,
                'stock': op.stock,
                'reserve': op.reserve,
            }
            for op in op_list
        ]
        for code, op_list in operations.items()
    })


def operation_from_cache(code: str, op_data: dict, user_id: int) -> Operation:
    op = Operation.__new__(Operation)

    state = ModelState()
    state.adding = False
    state.db = 'default'

    op._state = state
    op.id = op_data['id']
    op.user_id = user_id
    op.code = code
    op.date = datetime.strptime(op_data['date'], '%Y-%m-%d').date()
    op.sortOrder = op_data.get('sortOrder', 0)
    op.operationType = op_data['operationType']
    op.price = op_data['price']
    op.count = op_data['count']
    op.fee = op_data['fee']
    op.comment = op_data['comment']
    op.cash = op_data['cash']
    op.stock = op_data['stock']
    op.reserve = op_data['reserve']
    return op


def deserialize_operations(data: str, user: User) -> OperationDict:
    operations_dict = json.loads(data)
    user_id = user.id
    return {
        code: [operation_from_cache(code, op_data, user_id) for op_data in op_list]
        for code, op_list in operations_dict.items()
    }
