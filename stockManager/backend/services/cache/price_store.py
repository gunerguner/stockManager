"""股价缓存与刷新策略（分市场 CN / HK）"""
from datetime import datetime

from django.core.cache import cache

from ...common.cache import Cache
from ...common import logger
from ...common.market import Market, code_to_market, split_codes_by_market
from ...common.tradingCalendar import TZ_SHANGHAI
from ...common.types import MarketsData, RealtimePriceDict
from ..market.realtimePrice import fetch_prices
from . import keys
from . import meta_store
from . import refresh_policy
from . import user_store

_PRICE_FIELDS = frozenset({
    "name",
    "currentPrice",
    "priceOffset",
    "offsetRatio",
    "yesterdayClose",
    "yearHigh",
})


def get_markets_metadata() -> MarketsData:
    return {
        market.value: {
            "inTradingHours": refresh_policy.is_in_trading_hours(market),
            "priceUpdatedAt": refresh_policy.get_price_timestamp(market),
        }
        for market in Market
    }


def _price_key(code: str) -> str:
    return keys.KEY_STOCK_PRICE.format(code=code)


def _set_prices_timestamp_and_invalidate(markets: set[Market], timestamp: str) -> None:
    for market in markets:
        refresh_policy.set_price_timestamp(market, timestamp)
    user_store.clear_all_calculated_targets()


def _get_cached_prices(code_list: list[str]) -> tuple[dict[str, dict], list[str]]:
    if not code_list:
        return {}, []

    cached: dict[str, dict] = {}
    missing: list[str] = []
    for market, codes in zip((Market.CN, Market.HK), split_codes_by_market(code_list), strict=False):
        if not codes:
            continue
        if refresh_policy.should_refresh_market(market):
            missing.extend(codes)
            continue
        try:
            cache_keys = [_price_key(code) for code in codes]
            batch = Cache.get_many(cache_keys)
        except Exception as e:
            logger.error(f"批量获取股价缓存失败: {e}")
            batch = {key: cache.get(key) for key in cache_keys}
        for code, cache_key in zip(codes, cache_keys, strict=False):
            data = batch.get(cache_key)
            if data and _PRICE_FIELDS.issubset(data):
                cached[code] = data
            else:
                missing.append(code)
    return cached, missing


def _set_prices_batch(prices: dict[str, dict]) -> None:
    if not prices:
        return
    Cache.set_many(
        {_price_key(code): data for code, data in prices.items()},
        keys.TTL_STOCK_PRICE,
    )
    ts = datetime.now(TZ_SHANGHAI).isoformat()
    _set_prices_timestamp_and_invalidate(
        {code_to_market(code) for code in prices},
        ts,
    )


def query_prices(code_list: list[str]) -> RealtimePriceDict:
    cached, missing = _get_cached_prices(code_list)
    if not missing:
        return cached

    api_result = fetch_prices(missing)
    if api_result:
        _set_prices_batch(api_result)
        meta_store.sync_names_from_realtime(api_result)
    return {**cached, **api_result}
