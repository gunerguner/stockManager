"""股价缓存与刷新策略"""
from datetime import datetime

from django.core.cache import cache

from ...common.cache import Cache
from ...common import logger
from ...common.tradingCalendar import TradingCalendar, TZ_SHANGHAI
from . import keys


def should_refresh_cache() -> bool:
    """判断是否需要刷新股价缓存"""
    if TradingCalendar.is_current_time_in_trading_hours():
        return True

    cached_timestamp = get_stock_price_timestamp()
    if not cached_timestamp:
        return True

    cached_time = datetime.fromisoformat(cached_timestamp)
    current_time = datetime.now(TZ_SHANGHAI)
    return TradingCalendar.is_trading_time_passed(cached_time, current_time)


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


def get_stock_price_timestamp() -> str | None:
    return cache.get(keys.KEY_STOCK_PRICE_TIMESTAMP)


def set_stock_price_timestamp(timestamp: str) -> None:
    from . import user_store

    cache.set(keys.KEY_STOCK_PRICE_TIMESTAMP, timestamp, keys.TTL_STOCK_PRICE)
    user_store.clear_all_calculated_targets()


def get_stock_prices_with_cache(code_list: list[str]) -> tuple[dict[str, dict], list[str]]:
    if not code_list:
        return {}, []

    if should_refresh_cache():
        return {}, code_list.copy()

    batch_result = get_stock_prices_batch(code_list)
    cached_result = {
        code: price_data
        for code in code_list
        if (price_data := batch_result.get(code))
    }
    missing_codes = [code for code in code_list if code not in cached_result]
    return cached_result, missing_codes


def set_stock_prices_batch(prices: dict[str, dict], timestamp: str | None = None) -> None:
    if not prices:
        return

    Cache.set_many(
        {keys.KEY_STOCK_PRICE.format(code=code): price_data for code, price_data in prices.items()},
        keys.TTL_STOCK_PRICE,
    )

    set_stock_price_timestamp(timestamp or datetime.now(TZ_SHANGHAI).isoformat())
