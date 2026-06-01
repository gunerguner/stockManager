"""港币汇率缓存与刷新策略"""
from collections.abc import Iterable

from django.core.cache import cache

from ...common.market import markets_in_codes
from . import keys
from . import price_store


def should_refresh_fx(user_codes: Iterable[str]) -> bool:
    return price_store.any_market_in_trading_hours(markets_in_codes(user_codes))


def get_hkd_cny_cached() -> float | None:
    cached = cache.get(keys.KEY_FX_HKD_CNY)
    return float(cached) if cached is not None else None


def set_hkd_cny_cached(rate: float) -> None:
    cache.set(keys.KEY_FX_HKD_CNY, rate, keys.TTL_FX)
