"""交易日历工具模块"""
from typing import ClassVar, Optional
from datetime import datetime
import pytz
from exchange_calendars import get_calendar, ExchangeCalendar

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
        """检查两个时间区间是否重叠"""
        return start1 < end2 and start2 < end1
    
    @classmethod
    def is_trading_time_passed(cls, last_time: datetime, current_time: datetime) -> bool:
        """判断两个时间点之间是否经过了交易时间"""
        calendar = cls.get_calendar()
        last_time_tz = TZ_SHANGHAI.localize(last_time) if last_time.tzinfo is None else last_time.astimezone(TZ_SHANGHAI)
        current_time_tz = TZ_SHANGHAI.localize(current_time) if current_time.tzinfo is None else current_time.astimezone(TZ_SHANGHAI)
        
        if last_time_tz > current_time_tz:
            last_time_tz, current_time_tz = current_time_tz, last_time_tz
        
        schedule_df = calendar.schedule.loc[last_time_tz.date():current_time_tz.date()]
        if len(schedule_df) == 0:
            return False
        
        # 遍历每个交易日，检查是否与 A 股的两个交易时段有重叠
        for session_date, schedule_row in schedule_df.iterrows():
            session_date_only = session_date.date()
            
            # 构建上午交易时段：9:30 - 11:30
            morning_start = TZ_SHANGHAI.localize(datetime(session_date_only.year, session_date_only.month, session_date_only.day, 9, 30))
            morning_end = TZ_SHANGHAI.localize(datetime(session_date_only.year, session_date_only.month, session_date_only.day, 11, 30))
            
            # 构建下午交易时段：13:00 - 15:00
            afternoon_start = TZ_SHANGHAI.localize(datetime(session_date_only.year, session_date_only.month, session_date_only.day, 13, 0))
            afternoon_end = TZ_SHANGHAI.localize(datetime(session_date_only.year, session_date_only.month, session_date_only.day, 15, 0))
            
            if cls.is_time_intervals_overlap(last_time_tz, current_time_tz, morning_start, morning_end):
                return True
            if cls.is_time_intervals_overlap(last_time_tz, current_time_tz, afternoon_start, afternoon_end):
                return True
        
        # 如果所有交易日的交易时段都没有重叠，说明没有经过交易时间
        return False
    
    @staticmethod
    def is_in_trading_hours(dt: datetime) -> bool:
        """判断指定时间是否在A股交易时间内"""
        if dt.tzinfo is None:
            dt = TZ_SHANGHAI.localize(dt)
        else:
            dt = dt.astimezone(TZ_SHANGHAI)
        
        hour, minute = dt.hour, dt.minute
        return (9, 30) <= (hour, minute) < (11, 30) or (13, 0) <= (hour, minute) < (15, 0)


TradingCalendar.get_calendar()  # 预加载交易日历

