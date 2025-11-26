"""
交易日历工具模块
提供A股交易日历相关的工具函数
"""
from typing import ClassVar, Optional
from datetime import datetime
import pytz

from exchange_calendars import get_calendar, ExchangeCalendar

# A股时区（北京时间）
TZ_SHANGHAI = pytz.timezone('Asia/Shanghai')


class TradingCalendar:
    """交易日历工具类"""
    
    # 类变量：缓存交易日历对象，避免重复加载
    _calendar: ClassVar[Optional[ExchangeCalendar]] = None
    
    @classmethod
    def get_calendar(cls) -> ExchangeCalendar:
        """
        获取A股交易日历对象（带缓存）
        
        Returns:
            ExchangeCalendar: A股交易日历对象
        """
        if cls._calendar is None:
            cls._calendar = get_calendar('XSHG')
        return cls._calendar
    
    @staticmethod
    def is_time_intervals_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """
        检查两个时间区间 [start1, end1] 和 [start2, end2] 是否重叠
        
        Args:
            start1: 第一个区间的开始时间
            end1: 第一个区间的结束时间
            start2: 第二个区间的开始时间
            end2: 第二个区间的结束时间
            
        Returns:
            bool: 如果两个区间重叠返回 True，否则返回 False
        """
        return start1 < end2 and start2 < end1
    
    @classmethod
    def is_trading_time_passed(cls, last_time: datetime, current_time: datetime) -> bool:
        """
        判断两个时间点之间是否经过了交易时间
        
        Args:
            last_time: 上次时间
            current_time: 当前时间
            
        Returns:
            bool: 如果经过了交易时间返回 True，否则返回 False
        """
        # 获取A股交易日历（使用缓存，避免重复加载）
        calendar = cls.get_calendar()
        
        # 将时间转换为带时区的datetime（A股使用北京时间）
        last_time_tz = TZ_SHANGHAI.localize(last_time) if last_time.tzinfo is None else last_time.astimezone(TZ_SHANGHAI)
        current_time_tz = TZ_SHANGHAI.localize(current_time) if current_time.tzinfo is None else current_time.astimezone(TZ_SHANGHAI)
        
        # 确保 last_time <= current_time
        if last_time_tz > current_time_tz:
            last_time_tz, current_time_tz = current_time_tz, last_time_tz
        
        # 获取包含在日期范围内的所有交易日
        last_date = last_time_tz.date()
        current_date = current_time_tz.date()
        
        # 获取日期范围内的交易日历信息
        schedule_df = calendar.schedule.loc[last_date:current_date]
        
        # 如果没有交易日，说明都是非交易日，不需要更新
        if len(schedule_df) == 0:
            return False
        
        # 遍历每个交易日，检查是否与 A 股的两个交易时段有重叠
        for session_date, schedule_row in schedule_df.iterrows():
            # 获取交易日的日期部分
            session_date_only = session_date.date()
            
            # 构建上午交易时段：9:30 - 11:30
            morning_start = TZ_SHANGHAI.localize(datetime(session_date_only.year, session_date_only.month, session_date_only.day, 9, 30))
            morning_end = TZ_SHANGHAI.localize(datetime(session_date_only.year, session_date_only.month, session_date_only.day, 11, 30))
            
            # 构建下午交易时段：13:00 - 15:00
            afternoon_start = TZ_SHANGHAI.localize(datetime(session_date_only.year, session_date_only.month, session_date_only.day, 13, 0))
            afternoon_end = TZ_SHANGHAI.localize(datetime(session_date_only.year, session_date_only.month, session_date_only.day, 15, 0))
            
            # 检查 [last_time_tz, current_time_tz] 是否与上午交易时段重叠
            if cls.is_time_intervals_overlap(last_time_tz, current_time_tz, morning_start, morning_end):
                return True
            
            # 检查 [last_time_tz, current_time_tz] 是否与下午交易时段重叠
            if cls.is_time_intervals_overlap(last_time_tz, current_time_tz, afternoon_start, afternoon_end):
                return True
        
        # 如果所有交易日的交易时段都没有重叠，说明没有经过交易时间
        return False
    
    @staticmethod
    def is_in_trading_hours(dt: datetime) -> bool:
        """
        判断指定时间是否在A股交易时间内
        
        Args:
            dt: 要判断的时间
            
        Returns:
            bool: 如果在交易时间内返回 True
        """
        # 转换为北京时间
        if dt.tzinfo is None:
            dt = TZ_SHANGHAI.localize(dt)
        else:
            dt = dt.astimezone(TZ_SHANGHAI)
        
        hour = dt.hour
        minute = dt.minute
        
        # 上午交易时间：9:30 - 11:30
        morning_start = (9, 30)
        morning_end = (11, 30)
        
        # 下午交易时间：13:00 - 15:00
        afternoon_start = (13, 0)
        afternoon_end = (15, 0)
        
        # 判断是否在上午交易时间
        if (hour, minute) >= morning_start and (hour, minute) < morning_end:
            return True
        
        # 判断是否在下午交易时间
        if (hour, minute) >= afternoon_start and (hour, minute) < afternoon_end:
            return True
        
        return False


# 模块导入时预加载交易日历，避免首次使用时延迟
def _init_calendar():
    """初始化交易日历（模块导入时自动执行）"""
    TradingCalendar.get_calendar()


# 执行初始化（模块导入时自动执行）
_init_calendar()

