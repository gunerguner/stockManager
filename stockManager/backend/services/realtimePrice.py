"""
股票实时价格查询服务模块
提供股票实时价格查询功能，带缓存优化
"""
import urllib.request
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, ClassVar
from datetime import datetime

from ..common import logger
from ..common.tradingCalendar import TradingCalendar, TZ_SHANGHAI
from ..utils import _safe_float


@dataclass
class RealtimePriceData:
    """实时价格数据类（支持点号访问）"""
    name: str  # 股票名称
    currentPrice: float  # 现价
    priceOffset: float  # 涨跌额
    offsetRatio: str  # 涨跌幅（百分比字符串）
    yesterdayClose: float  # 昨收价

# 常量定义
STOCK_PRICE_API_URL = 'http://qt.gtimg.cn/q='
MIN_RESPONSE_LENGTH = 10
ENCODING_GB18030 = 'gb18030'


class RealtimePrice:
    """股票实时价格查询服务（使用类方法和类变量）"""
    
    # 类变量：缓存数据和缓存时间
    _cache: ClassVar[Dict[str, RealtimePriceData]] = {}
    _cache_timestamp: ClassVar[Optional[datetime]] = None
    
    @classmethod
    def _calculate_offset_ratio(cls, offset: float, base_price: float) -> str:
        """计算涨跌幅百分比"""
        if base_price == 0.0:
            return "0"
        ratio = (offset / base_price) * 100
        return f"{ratio:.2f}%"
    
    @classmethod
    def query(cls, code_list: List[str]) -> Dict[str, RealtimePriceData]:
        """
        查询股票实时价格（带缓存优化）
        
        使用内存缓存机制，如果缓存有效（未经过交易时间），直接返回缓存数据。
        如果经过了交易时间，重新获取数据并更新缓存。
        
        Args:
            code_list: 股票代码列表
            
        Returns:
            Dict[str, RealtimePriceData]: 股票代码到实时数据的映射
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
            if not TradingCalendar.is_trading_time_passed(cls._cache_timestamp, current_time):
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
                
                # 组装返回数据（直接使用转换后的 float 值，避免后续重复转换）
                result[missing_codes[index]] = RealtimePriceData(
                    name=stock_info[1],
                    currentPrice=current_price,
                    priceOffset=price_offset,
                    offsetRatio=offset_ratio,
                    yesterdayClose=yesterday_close
                )
            
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
    
    @staticmethod
    def get_default_data() -> RealtimePriceData:
        """获取默认的实时价格数据（用于数据缺失时）"""
        return RealtimePriceData(
            name="未知",
            currentPrice=0.0,
            priceOffset=0.0,
            offsetRatio="0%",
            yesterdayClose=0.0
        )



