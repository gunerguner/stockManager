"""行情刷新策略（交易时段、价格时间戳、缓存失效判断）"""
from collections.abc import Iterable
from datetime import datetime

from django.core.cache import cache

from ...common.market import Market
from ...common.tradingCalendar import TradingCalendar, TZ_SHANGHAI
from . import keys


def is_in_trading_hours(market: Market) -> bool:
    return TradingCalendar.is_in_trading_hours_at(datetime.now(TZ_SHANGHAI), market)


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
    """上次拉价至今是否经过该市场任意交易时段（含跨日、法定假日跳过）。"""
    ts = get_price_timestamp(market)
    if not ts:
        return True
    last_time = datetime.fromisoformat(ts)
    if last_time.tzinfo is None:
        last_time = TZ_SHANGHAI.localize(last_time)
    else:
        last_time = last_time.astimezone(TZ_SHANGHAI)
    return TradingCalendar.is_trading_time_passed(last_time, datetime.now(TZ_SHANGHAI), market)
