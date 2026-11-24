"""净值区间刷新：尾部重算、短历史退回全量、非法参数。"""
from datetime import date, timedelta

import pytest

from backend.common.domain.calendar import TradingCalendar
from backend.common.domain.market import Market
from backend.models import Operation, PortfolioNavDaily, StockMeta
from backend.services.app import nav as nav_mod
from backend.services.app.nav import NavAnalysis

SENTINEL_NAV = 7.77


def _closes_for_windows(windows):
    prices = {}
    for code, spans in windows.items():
        series = {}
        for start, stop in spans:
            for day in TradingCalendar.sessions_between(start, stop, Market.CN):
                series[day] = 10.0
        prices[code] = series
    return prices


@pytest.fixture
def closed_end(monkeypatch):
    end = TradingCalendar.sessions_between(date(2024, 6, 3), date(2024, 12, 31))[-1]
    monkeypatch.setattr(
        nav_mod.TradingCalendar,
        "latest_closed_session",
        classmethod(lambda cls, as_of=None, market=Market.CN: end),
    )
    monkeypatch.setattr(nav_mod, "ensure_daily_prices_for_windows", _closes_for_windows)
    monkeypatch.setattr(nav_mod, "ensure_hkd_cny_rates", lambda start, end: {})
    return end


def _sessions_through(end: date) -> list[date]:
    return TradingCalendar.sessions_between(date(2024, 1, 2), end)


def _seed_history(user, sessions: list[date]) -> None:
    meta = StockMeta.objects.create(code="sh600519", name="贵州茅台", stockType="SH60")
    Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=sessions[0],
        operationType="BUY",
        price="10",
        count=100,
    )
    Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=sessions[-3],
        operationType="BUY",
        price="12",
        count=100,
    )
    PortfolioNavDaily.objects.bulk_create(
        [
            PortfolioNavDaily(
                user=user,
                date=day,
                nav=SENTINEL_NAV,
                units=100,
                asset=1000,
                cash=0,
            )
            for day in sessions
        ]
    )


@pytest.mark.django_db
def test_recent_month_keeps_earlier_rows_and_shorter_span_writes_less(user, closed_end):
    sessions = _sessions_through(closed_end)
    _seed_history(user, sessions)

    month_start = closed_end - timedelta(days=31)
    NavAnalysis.refresh(user, mode="recent", span="month")

    earlier = list(
        PortfolioNavDaily.objects.filter(user=user, date__lt=month_start).values_list(
            "nav", flat=True
        )
    )
    assert earlier
    assert set(earlier) == {SENTINEL_NAV}
    assert PortfolioNavDaily.objects.filter(
        user=user, date__gte=month_start
    ).exclude(nav=SENTINEL_NAV).exists()

    week_written = NavAnalysis.refresh(user, mode="recent", span="week")
    quarter_written = NavAnalysis.refresh(user, mode="recent", span="quarter")
    assert 0 < week_written < quarter_written

    quarter_start = closed_end - timedelta(days=92)
    assert PortfolioNavDaily.objects.filter(
        user=user, date__lt=quarter_start, nav=SENTINEL_NAV
    ).exists()


@pytest.mark.django_db
def test_recent_without_seed_falls_back_to_full(user, closed_end):
    sessions = _sessions_through(closed_end)
    meta = StockMeta.objects.create(code="sh600519", name="贵州茅台", stockType="SH60")
    Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=sessions[-3],
        operationType="BUY",
        price="10",
        count=100,
    )
    PortfolioNavDaily.objects.create(
        user=user,
        date=sessions[-1],
        nav=SENTINEL_NAV,
        units=1,
        asset=1,
        cash=0,
    )
    decoy = closed_end - timedelta(days=3)
    PortfolioNavDaily.objects.create(
        user=user,
        date=decoy,
        nav=SENTINEL_NAV,
        units=1,
        asset=1,
        cash=0,
    )

    written = NavAnalysis.refresh(user, mode="recent", span="week")

    assert written > 1
    assert not PortfolioNavDaily.objects.filter(user=user, nav=SENTINEL_NAV).exists()
    assert not PortfolioNavDaily.objects.filter(user=user, date__lt=sessions[-3]).exists()


@pytest.mark.django_db
def test_refresh_rejects_bad_mode_and_span(user):
    with pytest.raises(ValueError, match="mode"):
        NavAnalysis.refresh(user, mode="boom")
    with pytest.raises(ValueError, match="span"):
        NavAnalysis.refresh(user, mode="recent", span="year")
    assert nav_mod._recent_span_name(None) == "month"
