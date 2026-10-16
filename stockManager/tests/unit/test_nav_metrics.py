from datetime import date

from backend.services.calculation.nav.metrics import apply_income_cash_display, compute_metrics


def test_empty_points_yield_empty_display_and_zero_metrics():
    assert apply_income_cash_display([], 10.0, 100.0) == []
    metrics = compute_metrics([])
    assert metrics["totalReturn"] == 0.0
    assert metrics["annualizedReturn"] == 0.0
    assert metrics["maxDrawdown"] == 0.0
    assert metrics["maxNav"] is None
    assert metrics["drawdown"] is None


def test_income_cash_is_linearly_spread_into_nav_display():
    points = [
        (date(2024, 1, 1), 1.0),
        (date(2024, 1, 2), 1.1),
        (date(2024, 1, 3), 1.2),
        (date(2024, 1, 4), 1.3),
    ]
    displayed = apply_income_cash_display(points, income_cash=100.0, origin_cash=100.0)
    daily_adj = 0.25
    assert displayed[0]["nav"] == 1.0
    assert displayed[0]["navDisplay"] == 1.0 + daily_adj
    assert displayed[3]["navDisplay"] == 1.3 + daily_adj * 4
    assert displayed[0]["date"] == "2024-01-01"


def test_max_drawdown_from_peak_to_trough():
    points = apply_income_cash_display(
        [
            (date(2024, 1, 1), 1.0),
            (date(2024, 1, 2), 1.1),
            (date(2024, 1, 3), 0.88),
            (date(2024, 1, 4), 1.12),
        ],
        income_cash=0.0,
        origin_cash=1000.0,
    )
    metrics = compute_metrics(points)
    max_nav = metrics["maxNav"]
    drawdown = metrics["drawdown"]
    assert metrics["totalReturn"] == 1.12 / 1.0 - 1.0
    assert metrics["maxDrawdown"] == 0.88 / 1.1 - 1.0
    assert max_nav is not None
    assert drawdown is not None
    assert max_nav["date"] == "2024-01-04"
    assert drawdown["peakDate"] == "2024-01-02"
    assert drawdown["troughDate"] == "2024-01-03"
    assert drawdown["recovered"] is True
