from datetime import date

from backend.services.calculation.nav.benchmarks import (
    align_benchmark_closes,
    benchmark_windows,
    nav_cache_has_benchmarks,
)
from backend.services.calculation.nav.metrics import assemble_nav_analysis


def test_align_keeps_anchor_close_and_leaves_missing_day_empty():
    dates = [date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)]
    closes = {
        "sh000300": {
            date(2024, 1, 2): 3000.0,
            date(2024, 1, 4): 3300.0,
        },
        "sz399006": {date(2024, 1, 2): 2000.0, date(2024, 1, 3): 2100.0},
        "sh000688": {date(2024, 1, 4): 1200.0},
    }
    aligned = align_benchmark_closes(dates, closes)
    assert aligned[0]["hs300"] == 3000.0
    assert aligned[1]["hs300"] is None
    assert aligned[2]["hs300"] == 3300.0
    assert aligned[0]["cyb"] == 2000.0
    assert aligned[0]["kc50"] is None
    assert aligned[2]["kc50"] == 1200.0


def test_align_does_not_fill_before_listing():
    dates = [date(2018, 1, 2), date(2020, 7, 23)]
    aligned = align_benchmark_closes(
        dates,
        {"sh000688": {date(2020, 7, 23): 1400.0}},
    )
    assert aligned[0]["kc50"] is None
    assert aligned[1]["kc50"] == 1400.0
    assert aligned[0]["hs300"] is None


def test_benchmark_windows_clip_to_listing_date():
    windows = benchmark_windows(date(2018, 1, 2), date(2024, 1, 4))
    assert windows["sh000300"] == [(date(2018, 1, 2), date(2024, 1, 4))]
    assert windows["sz399006"] == [(date(2018, 1, 2), date(2024, 1, 4))]
    assert windows["sh000688"] == [(date(2020, 7, 23), date(2024, 1, 4))]
    assert benchmark_windows(date(2024, 2, 1), date(2024, 1, 1)) == {}


def test_stale_cache_without_benchmarks_is_a_miss():
    assert nav_cache_has_benchmarks(None) is False
    assert nav_cache_has_benchmarks({"points": []}) is False
    assert nav_cache_has_benchmarks({"benchmarks": []}) is True


def test_assemble_attaches_benchmark_closes_on_each_point():
    result = assemble_nav_analysis(
        [(date(2024, 1, 2), 1.0), (date(2024, 1, 3), 1.1)],
        income_cash=0.0,
        origin_cash=1.0,
        benchmark_closes={"sh000300": {date(2024, 1, 2): 4000.0}},
    )
    assert result["benchmarks"][0]["code"] == "sh000300"
    assert result["points"][0]["benchmarks"]["hs300"] == 4000.0
    assert result["points"][1]["benchmarks"]["hs300"] is None
    assert result["points"][1]["benchmarks"]["kc50"] is None
