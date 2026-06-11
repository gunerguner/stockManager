"""交易日历工具模块（按市场 CN / HK 分离）

交易日判定以 exchange_calendars 的 XSHG / XHKG 为准，已包含：
- 周末
- 法定假日（周中休市，如春节、国庆等）
- 交易所公布的其他休市日

A 股调休上班日（补班）仍不开盘，亦不在 sessions 内。
"""
from typing import ClassVar
from datetime import datetime, timedelta
import pytz
from exchange_calendars import get_calendar, ExchangeCalendar
import pandas as pd

from backend.common.market import Market

TZ_SHANGHAI = pytz.timezone('Asia/Shanghai')

# 同日交易时段（上海时区；仅在 is_trading_day 为 True 的日期内生效）
_MARKET_SESSION_MINUTES: dict[Market, tuple[tuple[int, int], tuple[int, int]]] = {
    Market.CN: ((9 * 60 + 30, 11 * 60 + 30), (13 * 60, 15 * 60)),
    Market.HK: ((9 * 60 + 30, 12 * 60), (13 * 60, 16 * 60)),
}

_EXCHANGE_CODE: dict[Market, str] = {
    Market.CN: "XSHG",
    Market.HK: "XHKG",
}


def _to_shanghai(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return TZ_SHANGHAI.localize(dt)
    return dt.astimezone(TZ_SHANGHAI)


class TradingCalendar:
    """交易日历工具类"""
    _calendars: ClassVar[dict[Market, ExchangeCalendar]] = {}

    @classmethod
    def get_calendar(cls, market: Market = Market.CN) -> ExchangeCalendar:
        """获取指定市场的交易日历对象（带缓存）"""
        if market not in cls._calendars:
            cls._calendars[market] = get_calendar(_EXCHANGE_CODE[market])
        return cls._calendars[market]

    @classmethod
    def is_trading_day(cls, day, market: Market = Market.CN) -> bool:
        """是否为该市场的交易日（非法定假日、非周末、非交易所休市日）。"""
        return bool(cls.get_calendar(market).is_session(pd.Timestamp(day)))

    @classmethod
    def is_trading_time_passed(
        cls,
        last_time: datetime,
        current_time: datetime,
        market: Market = Market.CN,
    ) -> bool:
        """判断 [last_time, current_time] 是否与任意交易日的开收盘时段有交集。"""
        last_time_tz = _to_shanghai(last_time)
        current_time_tz = _to_shanghai(current_time)

        if last_time_tz >= current_time_tz:
            return False

        check_date = last_time_tz.date()
        end_date = current_time_tz.date()
        while check_date <= end_date:
            if cls.is_trading_day(check_date, market):
                for start_min, end_min in _MARKET_SESSION_MINUTES[market]:
                    session_start = TZ_SHANGHAI.localize(
                        datetime(check_date.year, check_date.month, check_date.day, start_min // 60, start_min % 60)
                    )
                    session_end = TZ_SHANGHAI.localize(
                        datetime(check_date.year, check_date.month, check_date.day, end_min // 60, end_min % 60)
                    )
                    if last_time_tz <= session_end and session_start <= current_time_tz:
                        return True
            check_date += timedelta(days=1)

        return False

    @classmethod
    def is_in_trading_hours_at(cls, dt: datetime, market: Market = Market.CN) -> bool:
        """判断给定时间是否在指定市场的交易时段内（交易日 + 固定开收盘时段）。"""
        dt_tz = _to_shanghai(dt)
        if not cls.is_trading_day(dt_tz.date(), market):
            return False
        current_minutes = dt_tz.hour * 60 + dt_tz.minute
        return any(
            start_min <= current_minutes < end_min
            for start_min, end_min in _MARKET_SESSION_MINUTES[market]
        )


TradingCalendar.get_calendar(Market.CN)
