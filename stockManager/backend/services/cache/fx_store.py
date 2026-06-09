"""港币汇率缓存与刷新策略"""
from collections.abc import Iterable

from django.core.cache import cache

from ...common.market import markets_in_codes
from ..market.exchangeRate import fetch_hkd_cny_rate
from . import keys
from . import price_store


def get_hkd_cny_rate(user_codes: Iterable[str]) -> float:
    if not price_store.any_market_in_trading_hours(markets_in_codes(user_codes)):
        cached = cache.get(keys.KEY_FX_HKD_CNY)
        if cached is not None:
            return float(cached)

    rate = fetch_hkd_cny_rate()
    cache.set(keys.KEY_FX_HKD_CNY, rate, keys.TTL_FX)
    return rate
