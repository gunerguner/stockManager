from datetime import date, timedelta

from backend.models import Operation
from backend.services.calculation.holdings.single_metrics import compute_single_metrics
from tests.helpers import make_meta, make_op


def test_buy_sets_hold_count_and_cost():
    meta = make_meta()
    ops = [
        make_op(meta, op_date=date(2024, 1, 2), price="10", count=100, fee="5"),
    ]
    metrics = compute_single_metrics(ops)
    assert metrics.current_hold_count == 100
    assert metrics.current_hold_cost == 10.05
    assert metrics.current_overall_cny == 1005.0
    assert metrics.total_fee_cny == 5.0


def test_clear_then_rebuy_resets_hold_cost():
    meta = make_meta()
    ops = [
        make_op(meta, op_date=date(2024, 1, 2), price="10", count=100, fee="0"),
        make_op(
            meta,
            op_date=date(2024, 1, 3),
            op_type=Operation.OperationType.SELL,
            price="12",
            count=100,
            fee="0",
        ),
        make_op(meta, op_date=date(2024, 1, 4), price="8", count=50, fee="0"),
    ]
    metrics = compute_single_metrics(ops)
    assert metrics.current_hold_count == 50
    assert metrics.current_hold_cost == 8.0
    assert metrics.current_overall_cny == 200.0


def test_dividend_cash_and_bonus_shares():
    meta = make_meta()
    ops = [
        make_op(meta, op_date=date(2024, 1, 2), price="10", count=100, fee="0"),
        make_op(
            meta,
            op_date=date(2024, 1, 10),
            op_type=Operation.OperationType.Dividend,
            cash="0.5",
            stock=0.1,
        ),
    ]
    metrics = compute_single_metrics(ops)
    assert metrics.current_hold_count == 110
    assert metrics.current_overall_cny == 950.0
    assert abs(metrics.current_hold_cost - 1000.0 / 110.0) < 1e-9


def test_hk_dual_ledger():
    meta = make_meta("hk00700", name="腾讯", stock_type="HK")
    ops = [
        make_op(
            meta,
            op_date=date(2024, 1, 2),
            price="300",
            count=100,
            fee="10",
            amount="25800",
        ),
    ]
    metrics = compute_single_metrics(ops, hkd_cny_rate=0.86)
    fx = 25800.0 / 30000.0
    assert metrics.current_hold_count == 100
    assert metrics.current_overall_cny == 25810.0
    assert abs(metrics.current_hold_cost - (30000.0 + 10.0 / fx) / 100.0) < 1e-9


def test_today_buy_uses_floating_pnl_as_today_offset():
    meta = make_meta()
    today = date.today()
    ops = [make_op(meta, op_date=today, price="10", count=100, fee="0")]
    metrics = compute_single_metrics(ops)
    assert metrics.yesterday_hold_count == 0
    assert metrics.today_input_cny == 1000.0
    assert metrics.offset_today_cny(1200.0, 0.0, price_now=12.0) == 200.0


def test_today_offset_with_yesterday_market_value():
    meta = make_meta()
    yesterday = date.today() - timedelta(days=1)
    ops = [make_op(meta, op_date=yesterday, price="10", count=100, fee="0")]
    metrics = compute_single_metrics(ops)
    assert metrics.yesterday_hold_count == 100
    assert metrics.today_input_cny == 0.0
    assert metrics.offset_today_cny(1200.0, 1100.0) == 100.0
