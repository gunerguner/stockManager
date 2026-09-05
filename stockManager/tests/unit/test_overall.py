from datetime import date, timedelta

from backend.services.calculation.holdings.overall import calculate_xirr, compute_overall


def _stock(*, offset_current=0.0, offset_total=0.0, total_value=0.0, offset_today=0.0, total_cost=0.0):
    return {
        "offsetCurrent": offset_current,
        "offsetTotal": offset_total,
        "totalValue": total_value,
        "totalOffsetToday": offset_today,
        "totalCost": total_cost,
    }


def test_overall_sums_cny_fields_and_income_cash():
    stocks = [
        _stock(offset_current=10, offset_total=20, total_value=100, offset_today=1, total_cost=2),
        _stock(offset_current=5, offset_total=-8, total_value=50, offset_today=-1, total_cost=1),
    ]
    cash_flows = [{"date": "2024-01-01", "amount": 1000.0}]
    overall = compute_overall(stocks, income_cash=30.0, cash_flow_list=cash_flows, hkd_cny_rate=0.9)
    assert overall["offsetCurrent"] == 15
    assert overall["offsetTotal"] == 42.0
    assert overall["totalValue"] == 150
    assert overall["offsetToday"] == 0
    assert overall["originCash"] == 1000.0
    assert overall["incomeCash"] == 30.0
    assert overall["totalAsset"] == 1042.0
    assert overall["totalCash"] == 892.0
    assert overall["hkdCnyRate"] == 0.9
    assert overall["cashFlowList"] == cash_flows


def test_xirr_empty_cash_flow_is_zero():
    assert calculate_xirr([], 1000.0) == 0.0
    assert calculate_xirr([{"date": "2024-01-01", "amount": 0}], 1000.0) == 0.0


def test_xirr_simple_positive_return_is_finite():
    past = (date.today() - timedelta(days=365)).isoformat()
    result = calculate_xirr([{"date": past, "amount": 10000.0}], 11000.0)
    assert result > 0
    assert result < 1.0
