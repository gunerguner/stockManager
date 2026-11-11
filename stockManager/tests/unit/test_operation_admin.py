from datetime import date

import pytest
from django.contrib.auth.models import User

from backend.admin.operation import OperationAdmin, OperationAdminForm
from backend.common.constants import OperationType
from backend.common.domain.operations import hold_count_before
from backend.models import Operation, StockMeta
from tests.helpers import make_meta, make_op


def _with_pk(operation: Operation, pk: int) -> Operation:
    operation.pk = pk
    return operation


def test_new_zero_sort_order_counts_later_same_day_operations():
    meta = make_meta()
    day = date(2024, 1, 2)
    earlier = _with_pk(make_op(meta, op_date=day, count=100, sort_order=0), 1)
    later = _with_pk(make_op(meta, op_date=day, count=50, sort_order=2), 2)
    after = _with_pk(make_op(meta, op_date=date(2024, 1, 3), count=80), 3)

    hold = hold_count_before(
        [after, later, earlier],
        on_date=day,
        sort_order=0,
        append_same_day=True,
    )

    assert hold == 150


def test_explicit_sort_order_stops_before_later_same_day_buy():
    meta = make_meta()
    day = date(2024, 1, 2)
    first = _with_pk(make_op(meta, op_date=day, count=100, sort_order=0), 1)
    second = _with_pk(make_op(meta, op_date=day, count=50, sort_order=2), 2)

    hold = hold_count_before(
        [first, second],
        on_date=day,
        sort_order=1,
    )

    assert hold == 100


def test_edit_excludes_itself_and_later_rows_with_the_same_order():
    meta = make_meta()
    day = date(2024, 1, 2)
    buy = _with_pk(make_op(meta, op_date=day, count=100, sort_order=0), 1)
    sell = _with_pk(
        make_op(
            meta,
            op_date=day,
            op_type=OperationType.SELL,
            count=40,
            sort_order=1,
        ),
        2,
    )
    later = _with_pk(make_op(meta, op_date=day, count=10, sort_order=1), 3)

    hold = hold_count_before(
        [buy, sell, later],
        on_date=day,
        sort_order=1,
        exclude_pk=sell.pk,
    )

    assert hold == 100


def test_fractional_hold_truncates_toward_zero():
    meta = make_meta()
    day = date(2024, 1, 2)
    buy = _with_pk(make_op(meta, op_date=day, count=10), 1)
    dividend = _with_pk(
        make_op(
            meta,
            op_date=date(2024, 1, 3),
            op_type=OperationType.DIVIDEND,
            stock=0.15,
        ),
        2,
    )

    hold = hold_count_before(
        [buy, dividend],
        on_date=date(2024, 1, 4),
        sort_order=0,
        append_same_day=True,
    )

    assert hold == 11


def test_sort_order_fieldset_is_collapsed_last():
    names = [name for name, _options in OperationAdmin.fieldsets]
    assert names[-1] == "同日顺序"
    basic = dict(OperationAdmin.fieldsets)["基本信息"]
    assert basic["fields"] == ("user", "stock_meta", "date", "operationType")
    sort_order = dict(OperationAdmin.fieldsets)["同日顺序"]
    assert sort_order["fields"] == ("sortOrder",)
    assert "collapse" in (sort_order.get("classes") or ())


def _sell_data(user, meta, *, count: int, on: date, sort_order: int = 0) -> dict:
    return {
        "user": user.pk,
        "stock_meta": meta.pk,
        "date": on.isoformat(),
        "sortOrder": str(sort_order),
        "operationType": OperationType.SELL.value,
        "price": "10",
        "count": str(count),
        "fee": "0",
        "comment": "",
        "cash": "0",
        "stock": "0",
        "reserve": "0",
    }


@pytest.mark.django_db
def test_sell_over_hold_is_rejected(user):
    meta = StockMeta.objects.create(code="sh600519", name="贵州茅台", stockType="SH60")
    day = date(2024, 1, 2)
    Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=day,
        operationType=OperationType.BUY,
        count=100,
    )
    form = OperationAdminForm(data=_sell_data(user, meta, count=101, on=day))

    assert form.is_valid() is False
    assert "不能超过持股数（当前 100）" in form.errors["count"][0]


@pytest.mark.django_db
def test_sell_equal_to_hold_is_accepted(user):
    meta = StockMeta.objects.create(code="sh600519", name="贵州茅台", stockType="SH60")
    day = date(2024, 1, 2)
    Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=day,
        operationType=OperationType.BUY,
        count=100,
    )
    form = OperationAdminForm(data=_sell_data(user, meta, count=100, on=day))

    assert form.is_valid() is True


@pytest.mark.django_db
def test_editing_sell_does_not_count_itself(user):
    meta = StockMeta.objects.create(code="sh600519", name="贵州茅台", stockType="SH60")
    day = date(2024, 1, 2)
    Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=day,
        operationType=OperationType.BUY,
        count=100,
        sortOrder=0,
    )
    sell = Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=day,
        operationType=OperationType.SELL,
        count=40,
        sortOrder=1,
    )
    form = OperationAdminForm(
        data=_sell_data(user, meta, count=100, on=day, sort_order=1),
        instance=sell,
    )

    assert form.is_valid() is True


@pytest.mark.django_db
def test_other_users_holdings_are_ignored(user):
    meta = StockMeta.objects.create(code="sh600519", name="贵州茅台", stockType="SH60")
    day = date(2024, 1, 2)
    other = User.objects.create_user(username="other", password="pass1234")
    Operation.objects.create(
        user=other,
        stock_meta=meta,
        date=day,
        operationType=OperationType.BUY,
        count=1000,
    )
    Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=day,
        operationType=OperationType.BUY,
        count=100,
    )
    form = OperationAdminForm(data=_sell_data(user, meta, count=101, on=day))

    assert form.is_valid() is False
    assert "当前 100" in form.errors["count"][0]


@pytest.mark.django_db
def test_sell_without_user_field_uses_actor(user):
    meta = StockMeta.objects.create(code="sh600519", name="贵州茅台", stockType="SH60")
    day = date(2024, 1, 2)
    Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=day,
        operationType=OperationType.BUY,
        count=100,
    )
    data = _sell_data(user, meta, count=101, on=day)
    del data["user"]
    form = OperationAdminForm(data=data)
    form.actor = user

    assert form.is_valid() is False
    assert "当前 100" in form.errors["count"][0]
