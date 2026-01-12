"""
股票实时价格查询服务模块
提供股票实时价格查询功能，带缓存优化
"""
import urllib.request
import re
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

from ..common import logger
from ..common.tradingCalendar import TradingCalendar, TZ_SHANGHAI
from ..common.utils import safe_float
from .cacheRepository import CacheRepository


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
    """股票实时价格查询服务（使用 Redis 缓存）"""
    
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
        查询股票实时价格（带 Redis 缓存）
        
        使用 Redis 缓存机制，如果缓存有效（未经过交易时间），直接返回缓存数据。
        如果经过了交易时间，重新获取数据并更新缓存。
        """
        if not code_list:
            return {}
        
        current_time = datetime.now(TZ_SHANGHAI)
        cached_result = {}
        missing_codes = []
        
        # 尝试从 Redis 获取缓存
        cached_timestamp = CacheRepository.get_stock_price_timestamp()
        
        if cached_timestamp:
            # 检查缓存是否有效
            cached_time = datetime.fromisoformat(cached_timestamp)
            if not TradingCalendar.is_trading_time_passed(cached_time, current_time):
                # 使用 Pipeline 批量获取
                batch_result = CacheRepository.get_stock_prices_batch(code_list)
                
                # 处理批量结果
                for code, price_data in batch_result.items():
                    if price_data:
                        cached_result[code] = RealtimePriceData(**price_data)
                    else:
                        missing_codes.append(code)
                
                if not missing_codes:
                    return cached_result
            else:
                missing_codes = code_list.copy()
        else:
            missing_codes = code_list.copy()
        
        # 从外部 API 获取
        try:
            url = STOCK_PRICE_API_URL + ','.join(missing_codes) + ','
            response_data = urllib.request.urlopen(url, timeout=10).read()
            response_array = str(response_data, encoding=ENCODING_GB18030).split(';')

            result = {}
            for index, single_response in enumerate(response_array):
                if len(single_response) <= MIN_RESPONSE_LENGTH:
                    continue
                    
                content_match = re.search(r'\"([^\"]*)\"', single_response)
                if not content_match:
                    continue
                    
                stock_info = content_match.group().strip('"').split('~')
                if len(stock_info) < 5:
                    continue
                
                current_price = safe_float(stock_info[3])
                yesterday_close = safe_float(stock_info[4])
                price_offset = current_price - yesterday_close
                offset_ratio = cls._calculate_offset_ratio(price_offset, yesterday_close)
                
                price_data = RealtimePriceData(
                    name=stock_info[1],
                    currentPrice=current_price,
                    priceOffset=price_offset,
                    offsetRatio=offset_ratio,
                    yesterdayClose=yesterday_close
                )
                result[missing_codes[index]] = price_data
                
                # 写入 Redis（TTL 由 CacheRepository 内部决定）
                CacheRepository.set_stock_price(
                    missing_codes[index],
                    {
                        'name': price_data.name,
                        'currentPrice': price_data.currentPrice,
                        'priceOffset': price_data.priceOffset,
                        'offsetRatio': price_data.offsetRatio,
                        'yesterdayClose': price_data.yesterdayClose,
                    }
                )
            
            # 更新时间戳
            CacheRepository.set_stock_price_timestamp(current_time.isoformat())
            
            return {**cached_result, **result}
            
        except urllib.error.URLError as e:
            logger.error(f"网络请求失败: {e}")
            if cached_result:
                return cached_result
            return {}
        except Exception as e:
            logger.error(f"查询实时价格失败: {e}")
            if cached_result:
                return cached_result
            return {}
    
    @classmethod
    def clear_cache(cls):
        """清空 Redis 缓存"""
        CacheRepository.clear_all_stock_prices()
    
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
