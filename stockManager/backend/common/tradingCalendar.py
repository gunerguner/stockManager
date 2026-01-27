"""交易日历工具模块"""
from typing import ClassVar, Optional
from datetime import datetime, timedelta
import pytz
from exchange_calendars import get_calendar, ExchangeCalendar
import pandas as pd

TZ_SHANGHAI = pytz.timezone('Asia/Shanghai')


class TradingCalendar:
    """交易日历工具类"""
    _calendar: ClassVar[Optional[ExchangeCalendar]] = None
    
    @classmethod
    def get_calendar(cls) -> ExchangeCalendar:
        """获取A股交易日历对象（带缓存）"""
        if cls._calendar is None:
            cls._calendar = get_calendar('XSHG')
        return cls._calendar
    
    @staticmethod
    def is_time_intervals_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """检查两个时间区间是否重叠（包含边界）"""
        return start1 <= end2 and start2 <= end1
    
    @classmethod
    def is_trading_time_passed(cls, last_time: datetime, current_time: datetime) -> bool:
        """判断两个时间点之间是否经过了交易时间"""
        calendar = cls.get_calendar()
        last_time_tz = TZ_SHANGHAI.localize(last_time) if last_time.tzinfo is None else last_time.astimezone(TZ_SHANGHAI)
        current_time_tz = TZ_SHANGHAI.localize(current_time) if current_time.tzinfo is None else current_time.astimezone(TZ_SHANGHAI)
        
        if last_time_tz > current_time_tz:
            last_time_tz, current_time_tz = current_time_tz, last_time_tz
        
        # 获取两个时间点所在的交易日
        last_date = last_time_tz.date()
        current_date_val = current_time_tz.date()
        
        # 如果是不同的日期,检查期间是否有交易日
        if last_date != current_date_val:
            # 遍历期间的每一天
            check_date = last_date
            while check_date <= current_date_val:
                # 使用 sessions 直接判断,避免 is_session() 的 BUG
                if pd.Timestamp(check_date) in calendar.sessions:
                    # 如果期间有交易日,则认为经过了交易时间
                    return True
                check_date += timedelta(days=1)
            return False
        
        # 如果是同一天,检查这一天是否是交易日,以及时间段是否经过交易时段
        # 使用 sessions 直接判断,避免 is_session() 的 BUG
        if pd.Timestamp(last_date) not in calendar.sessions:
            return False
        
        # 构建上午交易时段:9:30 - 11:30
        morning_start = TZ_SHANGHAI.localize(datetime(last_date.year, last_date.month, last_date.day, 9, 30))
        morning_end = TZ_SHANGHAI.localize(datetime(last_date.year, last_date.month, last_date.day, 11, 30))
        
        # 构建下午交易时段:13:00 - 15:00
        afternoon_start = TZ_SHANGHAI.localize(datetime(last_date.year, last_date.month, last_date.day, 13, 0))
        afternoon_end = TZ_SHANGHAI.localize(datetime(last_date.year, last_date.month, last_date.day, 15, 0))
        
        # 检查时间段是否与交易时段重叠
        if cls.is_time_intervals_overlap(last_time_tz, current_time_tz, morning_start, morning_end):
            return True
        if cls.is_time_intervals_overlap(last_time_tz, current_time_tz, afternoon_start, afternoon_end):
            return True
        
        return False
    
    @staticmethod
    def is_current_time_in_trading_hours() -> bool:
        """判断当前时间是否在A股交易时间内"""
        dt = datetime.now(TZ_SHANGHAI)
        
        calendar = TradingCalendar.get_calendar()
        # 转换为 pd.Timestamp 类型以满足 exchange_calendars 的要求
        return calendar.is_open_at_time(pd.Timestamp(dt))


TradingCalendar.get_calendar()  # 预加载交易日历

