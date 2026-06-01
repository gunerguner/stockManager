"""股价缓存与刷新策略（分市场 CN / HK）"""
from datetime import datetime
from typing import Iterable

from django.core.cache import cache

from ...common.cache import Cache
from ...common import logger
from ...common.market import Market, code_to_market, split_codes_by_market
from ...common.tradingCalendar import TradingCalendar, TZ_SHANGHAI
from . import keys


def _should_refresh_market(market: Market, *, relevant: bool) -> bool:
    """relevant=False：本批 code_list 不含此市场 → 不参与刷新判断"""
    if not relevant:
        return False
    if TradingCalendar.is_current_time_in_trading_hours(market):
        return True
    ts = get_stock_price_timestamp(market)
    if not ts:
        return True
    cached_time = datetime.fromisoformat(ts)
    return TradingCalendar.is_trading_time_passed(
        cached_time, datetime.now(TZ_SHANGHAI), market
    )


def should_refresh_cache() -> bool:
    """全局刷新判断（兼容旧调用；任一市场需刷新则返回 True）"""
    for market in Market:
        if _should_refresh_market(market, relevant=True):
            return True
    return False


def get_stock_price(code: str) -> dict | None:
    return cache.get(keys.KEY_STOCK_PRICE.format(code=code))


def get_stock_prices_batch(code_list: list[str]) -> dict[str, dict | None]:
    if not code_list:
        return {}
    try:
        cache_keys = [keys.KEY_STOCK_PRICE.format(code=code) for code in code_list]
        result = Cache.get_many(cache_keys)
        return {code: result.get(cache_keys[i]) for i, code in enumerate(code_list)}
    except Exception as e:
        logger.error(f"批量获取股价缓存失败: {e}")
        return {code: get_stock_price(code) for code in code_list}


def set_stock_price(code: str, price_data: dict) -> None:
    cache.set(keys.KEY_STOCK_PRICE.format(code=code), price_data, keys.TTL_STOCK_PRICE)


def get_stock_price_timestamp(market: Market) -> str | None:
    key = keys.KEY_STOCK_PRICE_TIMESTAMP.format(market=market.value)
    ts = cache.get(key)
    if ts:
        return ts
    if market == Market.CN:
        legacy = cache.get(keys.KEY_STOCK_PRICE_TIMESTAMP_LEGACY)
        if legacy:
            cache.set(key, legacy, keys.TTL_STOCK_PRICE)
            cache.delete(keys.KEY_STOCK_PRICE_TIMESTAMP_LEGACY)
            return legacy
    return None


def set_stock_price_timestamp(market: Market, timestamp: str) -> None:
    from . import user_store

    cache.set(
        keys.KEY_STOCK_PRICE_TIMESTAMP.format(market=market.value),
        timestamp,
        keys.TTL_STOCK_PRICE,
    )
    user_store.clear_all_calculated_targets()


def get_stock_prices_with_cache(code_list: list[str]) -> tuple[dict[str, dict], list[str]]:
    if not code_list:
        return {}, []

    cn_codes, hk_codes = split_codes_by_market(code_list)
    involved_markets = {code_to_market(c) for c in code_list}

    cached_result: dict[str, dict] = {}
    missing_codes: list[str] = []

    for market, codes in ((Market.CN, cn_codes), (Market.HK, hk_codes)):
        if not codes:
            continue
        relevant = market in involved_markets
        if _should_refresh_market(market, relevant=relevant):
            missing_codes.extend(codes)
            continue
        batch_result = get_stock_prices_batch(codes)
        for code in codes:
            price_data = batch_result.get(code)
            if price_data:
                cached_result[code] = price_data
            else:
                missing_codes.append(code)

    return cached_result, missing_codes


def set_stock_prices_batch(prices: dict[str, dict], timestamp: str | None = None) -> None:
    if not prices:
        return

    Cache.set_many(
        {keys.KEY_STOCK_PRICE.format(code=code): price_data for code, price_data in prices.items()},
        keys.TTL_STOCK_PRICE,
    )

    ts = timestamp or datetime.now(TZ_SHANGHAI).isoformat()
    markets_updated = {code_to_market(code) for code in prices}
    for market in markets_updated:
        set_stock_price_timestamp(market, ts)
