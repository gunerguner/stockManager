"""交易日历工具模块（按市场 CN / HK 分离）

交易日判定以 exchange_calendars 的 XSHG / XHKG 为准，已包含：
- 周末
- 法定假日（周中休市，如春节、国庆等）
- 交易所公布的其他休市日

A 股调休上班日（补班）仍不开盘，亦不在 sessions 内。
"""
from typing import ClassVar
from datetime import datetime, timedelta
import math
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

    @classmethod
    def next_open_at(cls, after: datetime, market: Market = Market.CN) -> datetime:
        """返回严格晚于 after 的最早一个交易时段开盘时刻（上海时区）。覆盖盘前、午休、盘后与非交易日情形，统一指向下一交易时段 start。"""
        tz_now = _to_shanghai(after)
        check_date = tz_now.date()
        # 防御性上限：连续非交易日（含长假）必然在 100 天内命中
        for _ in range(100):
            if cls.is_trading_day(check_date, market):
                for start_min, _end_min in _MARKET_SESSION_MINUTES[market]:
                    session_start = TZ_SHANGHAI.localize(
                        datetime(
                            check_date.year, check_date.month, check_date.day,
                            start_min // 60, start_min % 60,
                        )
                    )
                    if session_start > tz_now:
                        return session_start
            check_date += timedelta(days=1)
        raise RuntimeError(f"未找到 {market} 在 100 天内的开盘时段")


# ==================== 交易状态 Tag 生成（供 /api/tradingStatus 使用） ====================

_MARKET_LABEL: dict[Market, str] = {
    Market.CN: 'A股',
    Market.HK: '港股',
}


def _format_minutes_to_human(minutes: int) -> str:
    """把分钟数格式化为「天/小时/分钟」中文文案，与前端原 formatMinutes 一致。"""
    if minutes < 60:
        return f"{minutes} 分钟"

    hours = minutes // 60
    mins = minutes % 60

    if hours < 24:
        return f"{hours} 小时 {mins} 分钟" if mins > 0 else f"{hours} 小时"

    days = hours // 24
    hrs = hours % 24
    parts = [f"{days} 天" if days > 0 else None,
             f"{hrs} 小时" if hrs > 0 else None,
             f"{mins} 分钟" if mins > 0 else None]
    return ' '.join(p for p in parts if p)


def get_trading_time_statuses(now: datetime | None = None) -> list[dict]:
    """生成各市场交易状态 Tag 数据（供 /api/tradingStatus）。

    返回 [{'market':'cn', 'isTrading':bool, 'message':str}, {'market':'hk', ...}]。
    """
    if now is None:
        now = datetime.now(TZ_SHANGHAI)
    now_tz = _to_shanghai(now)
    current_minutes = now_tz.hour * 60 + now_tz.minute

    results: list[dict] = []
    for market in (Market.CN, Market.HK):
        periods = _MARKET_SESSION_MINUTES[market]
        (_morning_open, morning_close) = periods[0]
        (_afternoon_open, afternoon_close) = periods[1]
        label = _MARKET_LABEL[market]
        is_trading = TradingCalendar.is_in_trading_hours_at(now_tz, market)

        if is_trading:
            close_minutes = morning_close if current_minutes < morning_close else afternoon_close
            minutes_to_close = close_minutes - current_minutes
            message = f"{label} 距收盘 {_format_minutes_to_human(minutes_to_close)}"
        else:
            nxt_open = TradingCalendar.next_open_at(now_tz, market)
            delta_seconds = (nxt_open - now_tz).total_seconds()
            minutes_to_open = math.ceil(delta_seconds / 60)
            message = f"{label} 距开盘 {_format_minutes_to_human(minutes_to_open)}"

        results.append({
            'market': market.value,
            'isTrading': is_trading,
            'message': message,
        })
    return results


TradingCalendar.get_calendar(Market.CN)
