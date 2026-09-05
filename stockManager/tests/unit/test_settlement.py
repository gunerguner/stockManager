from datetime import date

import pytest

from backend.common.domain.settlement import (
    buy_cost_native,
    buy_outflow_cny,
    fee_in_price_currency,
    implied_fx,
    trade_amount_cny,
    trade_notional_hkd,
)
from tests.helpers import make_meta, make_op


def test_a_share_amount_is_price_times_count():
    meta = make_meta("sh600519")
    op = make_op(meta, op_date=date(2024, 1, 2), price="10.5", count=100, fee="5")
    assert trade_notional_hkd(op) == 1050.0
    assert trade_amount_cny(op) == 1050.0
    assert implied_fx(op) == 1.0
    assert fee_in_price_currency(op) == 5.0
    assert buy_outflow_cny(op) == 1055.0
    assert buy_cost_native(op) == 1055.0


def test_hk_uses_amount_as_cny_and_implied_fx():
    meta = make_meta("hk00700", name="腾讯", stock_type="HK")
    op = make_op(
        meta,
        op_date=date(2024, 1, 2),
        price="300",
        count=100,
        fee="10",
        amount="25800",
    )
    fx = 25800.0 / 30000.0
    assert trade_notional_hkd(op) == 30000.0
    assert trade_amount_cny(op) == 25800.0
    assert implied_fx(op) == pytest.approx(fx)
    assert fee_in_price_currency(op) == pytest.approx(10.0 / fx)
    assert buy_outflow_cny(op) == 25810.0


def test_hk_invalid_notional_implied_fx_is_zero():
    meta = make_meta("hk00700", stock_type="HK")
    op = make_op(meta, op_date=date(2024, 1, 2), price="0", count=0, amount="100")
    assert implied_fx(op) == 0.0
    assert fee_in_price_currency(op) == 0.0
