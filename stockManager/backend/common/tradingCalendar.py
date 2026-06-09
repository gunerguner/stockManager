"""交易日历工具模块（按市场 CN / HK 分离）"""
from typing import ClassVar
from datetime import datetime, timedelta
import pytz
from exchange_calendars import get_calendar, ExchangeCalendar
import pandas as pd

from .market import Market

TZ_SHANGHAI = pytz.timezone('Asia/Shanghai')

# 同日交易时段（上海时区，与 exchange_calendars 会话配合）
_MARKET_SESSION_MINUTES: dict[Market, tuple[tuple[int, int], tuple[int, int]]] = {
    Market.CN: ((9 * 60 + 30, 11 * 60 + 30), (13 * 60, 15 * 60)),
    Market.HK: ((9 * 60 + 30, 12 * 60), (13 * 60, 16 * 60)),
}

_EXCHANGE_CODE: dict[Market, str] = {
    Market.CN: "XSHG",
    Market.HK: "XHKG",
}


class TradingCalendar:
    """交易日历工具类"""
    _calendars: ClassVar[dict[Market, ExchangeCalendar]] = {}

    @classmethod
    def get_calendar(cls, market: Market = Market.CN) -> ExchangeCalendar:
        """获取指定市场的交易日历对象（带缓存）"""
        if market not in cls._calendars:
            cls._calendars[market] = get_calendar(_EXCHANGE_CODE[market])
        return cls._calendars[market]

    @staticmethod
    def is_time_intervals_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """检查两个时间区间是否重叠（包含边界）"""
        return start1 <= end2 and start2 <= end1

    @classmethod
    def is_trading_time_passed(
        cls,
        last_time: datetime,
        current_time: datetime,
        market: Market = Market.CN,
    ) -> bool:
        """判断两个时间点之间是否经过了指定市场的交易时间"""
        calendar = cls.get_calendar(market)
        last_time_tz = TZ_SHANGHAI.localize(last_time) if last_time.tzinfo is None else last_time.astimezone(TZ_SHANGHAI)
        current_time_tz = TZ_SHANGHAI.localize(current_time) if current_time.tzinfo is None else current_time.astimezone(TZ_SHANGHAI)

        if last_time_tz > current_time_tz:
            last_time_tz, current_time_tz = current_time_tz, last_time_tz

        last_date = last_time_tz.date()
        current_date_val = current_time_tz.date()

        if last_date != current_date_val:
            check_date = last_date
            while check_date <= current_date_val:
                if pd.Timestamp(check_date) in calendar.sessions:
                    return True
                check_date += timedelta(days=1)
            return False

        if pd.Timestamp(last_date) not in calendar.sessions:
            return False

        morning_start_min, morning_end_min = _MARKET_SESSION_MINUTES[market][0]
        afternoon_start_min, afternoon_end_min = _MARKET_SESSION_MINUTES[market][1]

        morning_start = TZ_SHANGHAI.localize(
            datetime(last_date.year, last_date.month, last_date.day, morning_start_min // 60, morning_start_min % 60)
        )
        morning_end = TZ_SHANGHAI.localize(
            datetime(last_date.year, last_date.month, last_date.day, morning_end_min // 60, morning_end_min % 60)
        )
        afternoon_start = TZ_SHANGHAI.localize(
            datetime(last_date.year, last_date.month, last_date.day, afternoon_start_min // 60, afternoon_start_min % 60)
        )
        afternoon_end = TZ_SHANGHAI.localize(
            datetime(last_date.year, last_date.month, last_date.day, afternoon_end_min // 60, afternoon_end_min % 60)
        )

        if cls.is_time_intervals_overlap(last_time_tz, current_time_tz, morning_start, morning_end):
            return True
        if cls.is_time_intervals_overlap(last_time_tz, current_time_tz, afternoon_start, afternoon_end):
            return True

        return False

    @classmethod
    def is_current_time_in_trading_hours(cls, market: Market = Market.CN) -> bool:
        """判断当前时间是否在指定市场的交易时间内"""
        dt = datetime.now(TZ_SHANGHAI)
        calendar = cls.get_calendar(market)
        return calendar.is_open_at_time(pd.Timestamp(dt))


TradingCalendar.get_calendar(Market.CN)
