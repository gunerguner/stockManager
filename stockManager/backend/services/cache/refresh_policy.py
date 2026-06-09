"""行情刷新策略（交易时段、价格时间戳、缓存失效判断）"""
from collections.abc import Iterable
from datetime import datetime

from django.core.cache import cache

from ...common.market import Market
from ...common.tradingCalendar import TradingCalendar, TZ_SHANGHAI
from . import keys


def is_in_trading_hours(market: Market) -> bool:
    return TradingCalendar.is_current_time_in_trading_hours(market)


def any_market_in_trading_hours(markets: Iterable[Market]) -> bool:
    return any(is_in_trading_hours(m) for m in markets)


def get_price_timestamp(market: Market) -> str | None:
    return cache.get(keys.KEY_STOCK_PRICE_TIMESTAMP.format(market=market.value))


def set_price_timestamp(market: Market, timestamp: str) -> None:
    cache.set(
        keys.KEY_STOCK_PRICE_TIMESTAMP.format(market=market.value),
        timestamp,
        keys.TTL_STOCK_PRICE,
    )


def should_refresh_market(market: Market) -> bool:
    if is_in_trading_hours(market):
        return True
    ts = get_price_timestamp(market)
    if not ts:
        return True
    return TradingCalendar.is_trading_time_passed(
        datetime.fromisoformat(ts), datetime.now(TZ_SHANGHAI), market
    )
