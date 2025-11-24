"""
股票实时价格查询服务模块
提供股票实时价格查询功能，带缓存优化
"""
import urllib.request
import re
from typing import Dict, List, Optional, ClassVar
from datetime import datetime
import pytz

from exchange_calendars import get_calendar

from ..common import logger
from ..utils import _safe_float

# 常量定义
STOCK_PRICE_API_URL = 'http://qt.gtimg.cn/q='
MIN_RESPONSE_LENGTH = 10
ENCODING_GB18030 = 'gb18030'

# A股时区（北京时间）
TZ_SHANGHAI = pytz.timezone('Asia/Shanghai')


class RealtimePrice:
    """股票实时价格查询服务（使用类方法和类变量）"""
    
    # 类变量：缓存数据和缓存时间
    _cache: ClassVar[Dict[str, List]] = {}
    _cache_timestamp: ClassVar[Optional[datetime]] = None
    
    # 类变量：缓存交易日历对象，避免重复加载
    _calendar: ClassVar[Optional[object]] = None
    
    @classmethod
    def _get_calendar(cls):
        """获取交易日历对象（带缓存）"""
        if cls._calendar is None:
            cls._calendar = get_calendar('XSHG')
        return cls._calendar
    
    @staticmethod
    def _is_time_intervals_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """
        检查两个时间区间 [start1, end1] 和 [start2, end2] 是否重叠
        """
        return start1 < end2 and start2 < end1
    
    @classmethod
    def _is_trading_time_passed(cls, last_time: datetime, current_time: datetime) -> bool:
        """
        判断两个时间点之间是否经过了交易时间
        
        Args:
            last_time: 上次缓存时间
            current_time: 当前时间
            
        Returns:
            bool: 如果经过了交易时间返回 True，否则返回 False
        """
        # 获取A股交易日历（使用缓存，避免重复加载）
        calendar = cls._get_calendar()
        
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
            if cls._is_time_intervals_overlap(last_time_tz, current_time_tz, morning_start, morning_end):
                return True
            
            # 检查 [last_time_tz, current_time_tz] 是否与下午交易时段重叠
            if cls._is_time_intervals_overlap(last_time_tz, current_time_tz, afternoon_start, afternoon_end):
                return True
        
        # 如果所有交易日的交易时段都没有重叠，说明没有经过交易时间
        return False
    
    @classmethod
    def _is_in_trading_hours(cls, dt: datetime) -> bool:
        """
        判断指定时间是否在A股交易时间内
        
        Args:
            dt: 要判断的时间（带时区）
            
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
    
    @classmethod
    def _calculate_offset_ratio(cls, offset: float, base_price: float) -> str:
        """计算涨跌幅百分比"""
        if base_price == 0.0:
            return "0"
        ratio = (offset / base_price) * 100
        return f"{ratio:.2f}%"
    
    @classmethod
    def query(cls, code_list: List[str]) -> Dict[str, List]:
        """
        查询股票实时价格（带缓存优化）
        
        使用内存缓存机制，如果缓存有效（未经过交易时间），直接返回缓存数据。
        如果经过了交易时间，重新获取数据并更新缓存。
        
        Args:
            code_list: 股票代码列表
            
        Returns:
            Dict[str, List]: 股票代码到实时数据的映射
            实时数据格式: [名称, 现价, 涨跌额, 涨跌幅, 昨收]
        """
        if not code_list:
            return {}
        
        # 获取当前时间（北京时间）
        current_time = datetime.now(TZ_SHANGHAI)
        
        # 检查缓存是否有效
        cached_result = {}
        missing_codes = code_list.copy()
        
        if cls._cache and cls._cache_timestamp is not None:
            # 检查是否经过了交易时间
            if not cls._is_trading_time_passed(cls._cache_timestamp, current_time):
                # 缓存有效，从缓存中提取已有的股票代码数据
                cached_result = {
                    code: cls._cache[code]
                    for code in code_list
                    if code in cls._cache and cls._cache[code] is not None
                }
                
                # 计算缺失的股票代码（只获取缓存中没有的）
                missing_codes = [code for code in code_list if code not in cached_result]
                
                # 如果所有请求的股票代码都在缓存中，直接返回
                if not missing_codes:
                    logger.debug(f"使用缓存数据，缓存时间: {cls._cache_timestamp}")
                    return cached_result
        
        # 如果有缺失的股票代码，只获取缺失的部分
        if not missing_codes:
            # 如果没有缺失的，直接返回缓存结果（虽然理论上不应该到这里）
            return cached_result
        
        try:
            # 构建请求URL（只获取缺失的股票代码）
            url = STOCK_PRICE_API_URL + ','.join(missing_codes) + ','
            
            # 发送请求并获取响应
            response_data = urllib.request.urlopen(url, timeout=10).read()
            response_array = str(response_data, encoding=ENCODING_GB18030).split(';')

            result = {}
            for index, single_response in enumerate(response_array):
                if len(single_response) <= MIN_RESPONSE_LENGTH:
                    continue
                    
                # 提取引号内的内容
                content_match = re.search(r'\"([^\"]*)\"', single_response)
                if not content_match:
                    continue
                    
                # 解析股票信息
                stock_info = content_match.group().strip('"').split('~')
                
                if len(stock_info) < 5:
                    logger.warning(f"股票 {missing_codes[index]} 数据格式不完整")
                    continue
                
                # 计算涨跌信息
                current_price = _safe_float(stock_info[3])
                yesterday_close = _safe_float(stock_info[4])
                price_offset = current_price - yesterday_close
                
                # 计算涨跌幅
                offset_ratio = cls._calculate_offset_ratio(price_offset, yesterday_close)
                
                # 组装返回数据: [名称, 现价, 涨跌额, 涨跌幅, 昨收]
                result[missing_codes[index]] = [
                    stock_info[1],
                    stock_info[3],
                    price_offset,
                    offset_ratio,
                    stock_info[4]
                ]
            
            # 更新缓存（只更新新获取的股票代码）
            cls._cache.update(result)
            cls._cache_timestamp = current_time
            logger.debug(f"更新缓存数据，时间: {cls._cache_timestamp}，新增: {len(result)} 个股票")
            
            # 合并缓存结果和新获取的结果
            return {**cached_result, **result}
            
        except urllib.error.URLError as e:
            logger.error(f"网络请求失败: {e}")
            # 如果网络请求失败，尝试返回缓存数据（如果有）
            if cached_result:
                logger.warning("网络请求失败，尝试返回缓存数据")
                return cached_result
            return {}
        except Exception as e:
            logger.error(f"查询实时价格失败: {e}")
            # 如果请求失败，尝试返回缓存数据（如果有）
            if cached_result:
                logger.warning("查询失败，尝试返回缓存数据")
                return cached_result
            return {}
    
    @classmethod
    def clear_cache(cls):
        """清空缓存（下次访问时会重新加载）"""
        cls._cache = {}
        cls._cache_timestamp = None

