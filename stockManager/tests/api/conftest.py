"""API 测试默认 mock 行情 / 汇率 / 估值，禁止出网。"""
import pytest

from backend.services.cache.repository import WatchlistMarketData


@pytest.fixture(autouse=True)
def mock_market_io(monkeypatch):
    def fake_prices(codes):
        return {
            code: {
                "name": code,
                "currentPrice": 10.0,
                "priceOffset": 0.2,
                "offsetRatio": 0.02,
                "yesterdayClose": 9.8,
            }
            for code in codes
        }

    monkeypatch.setattr(
        "backend.services.cache.market.prices.query_prices", fake_prices
    )
    monkeypatch.setattr(
        "backend.services.cache.market.fx.get_hkd_cny_rate", lambda _codes: 0.86
    )
    monkeypatch.setattr(
        "backend.services.cache.market.prices.get_markets_metadata",
        lambda: {
            "cn": {"inTradingHours": False, "priceUpdatedAt": None},
            "hk": {"inTradingHours": False, "priceUpdatedAt": None},
        },
    )
    monkeypatch.setattr(
        "backend.services.cache.market.valuation.get_cached_valuations",
        lambda codes: ({code: {} for code in codes}, []),
    )
    monkeypatch.setattr(
        "backend.services.cache.market.hist_high.get_cached_hist_highs",
        lambda codes: ({code: None for code in codes}, []),
    )
    monkeypatch.setattr(
        "backend.services.cache.repository.CacheRepository.load_watchlist_market_data",
        classmethod(
            lambda cls, codes: WatchlistMarketData(
                prices=fake_prices(codes),
                valuations={code: {} for code in codes},
                hist_highs={code: None for code in codes},
            )
        ),
    )
