"""股价缓存与刷新策略（分市场 CN / HK）"""
from datetime import datetime

from django.core.cache import cache

from backend.common.cache import Cache
from backend.common import logger
from backend.common.market import Market, split_codes_by_market
from backend.common.tradingCalendar import TZ_SHANGHAI
from backend.common.types import MarketsData, RealtimePriceDict
from backend.services.market.realtimePrice import fetch_prices
from backend.services.cache import keys
from backend.services.cache import meta_store
from backend.services.cache import refresh_policy
from backend.services.cache import user_store

_PRICE_FIELDS = frozenset({
    "name",
    "currentPrice",
    "priceOffset",
    "offsetRatio",
    "yesterdayClose",
    "yearHigh",
})

_MARKET_PRICE_PATTERNS: dict[Market, tuple[str, ...]] = {
    Market.CN: ("stock:price:sh*", "stock:price:sz*", "stock:price:bj*"),
    Market.HK: ("stock:price:hk*",),
}


def get_markets_metadata() -> MarketsData:
    return {
        "cn": {
            "inTradingHours": refresh_policy.is_in_trading_hours(Market.CN),
            "priceUpdatedAt": refresh_policy.get_price_timestamp(Market.CN),
        },
        "hk": {
            "inTradingHours": refresh_policy.is_in_trading_hours(Market.HK),
            "priceUpdatedAt": refresh_policy.get_price_timestamp(Market.HK),
        },
    }


def _price_key(code: str) -> str:
    return keys.KEY_STOCK_PRICE.format(code=code)


def _evict_market_prices(market: Market) -> None:
    """市场需刷新时清掉该市场全部单票价格，避免部分代码回源后推进时间戳、其余旧价永久命中。"""
    for pattern in _MARKET_PRICE_PATTERNS[market]:
        Cache.delete_pattern(pattern)


def _set_prices_timestamp_and_invalidate(markets: set[Market], timestamp: str) -> None:
    for market in markets:
        refresh_policy.set_price_timestamp(market, timestamp)
    user_store.clear_all_calculated_targets()


def _markets_fully_fetched(missing: list[str], api_result: RealtimePriceDict) -> set[Market]:
    """仅当某市场本次 missing 全部回源成功时，才允许推进该市场价格时间戳。"""
    complete: set[Market] = set()
    for market, codes in zip((Market.CN, Market.HK), split_codes_by_market(missing), strict=False):
        if codes and all(code in api_result for code in codes):
            complete.add(market)
    return complete


def _get_cached_prices(code_list: list[str]) -> tuple[RealtimePriceDict, list[str]]:
    if not code_list:
        return {}, []

    cached: RealtimePriceDict = {}
    missing: list[str] = []
    for market, codes in zip((Market.CN, Market.HK), split_codes_by_market(code_list), strict=False):
        if not codes:
            continue
        if refresh_policy.should_refresh_market(market):
            _evict_market_prices(market)
            missing.extend(codes)
            continue
        cache_keys = [_price_key(code) for code in codes]
        try:
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


def _set_prices_batch(prices: RealtimePriceDict, markets_to_timestamp: set[Market]) -> None:
    if not prices:
        return
    Cache.set_many(
        {_price_key(code): data for code, data in prices.items()},
        keys.TTL_STOCK_PRICE,
    )
    if not markets_to_timestamp:
        return
    ts = datetime.now(TZ_SHANGHAI).isoformat()
    _set_prices_timestamp_and_invalidate(markets_to_timestamp, ts)


def query_prices(code_list: list[str]) -> RealtimePriceDict:
    cached, missing = _get_cached_prices(code_list)
    if not missing:
        return cached

    api_result = fetch_prices(missing)
    if api_result:
        _set_prices_batch(api_result, _markets_fully_fetched(missing, api_result))
        meta_store.sync_names_from_realtime(api_result)
    return {**cached, **api_result}
