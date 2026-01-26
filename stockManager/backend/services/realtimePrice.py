"""股票实时价格查询服务模块"""
import urllib.request
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from ..common import logger
from ..common.utils import safe_float
from .cacheRepository import CacheRepository


@dataclass
class RealtimePriceData:
    """实时价格数据"""
    name: str
    currentPrice: float
    priceOffset: float
    offsetRatio: str
    yesterdayClose: float
    
    def to_cache_dict(self) -> Dict:
        return asdict(self)


STOCK_PRICE_API_URL = 'http://qt.gtimg.cn/q='
MIN_RESPONSE_LENGTH = 10
ENCODING_GB18030 = 'gb18030'


class RealtimePrice:
    """股票实时价格查询服务"""
    
    @classmethod
    def _calculate_offset_ratio(cls, offset: float, base_price: float) -> str:
        if base_price == 0.0:
            return "0"
        return f"{(offset / base_price) * 100:.2f}%"
    
    @classmethod
    def query(cls, code_list: List[str]) -> Dict[str, RealtimePriceData]:
        """查询股票实时价格"""
        if not code_list:
            return {}
        
        cached_data, missing_codes = CacheRepository.get_stock_prices_with_cache(code_list)
        result = {code: RealtimePriceData(**data) for code, data in cached_data.items()}
        
        if missing_codes:
            api_result = cls.fetch_from_api(missing_codes)
            if api_result:
                CacheRepository.set_stock_prices_batch(
                    {code: data.to_cache_dict() for code, data in api_result.items()}
                )
                result.update(api_result)
        
        return result
    
    @classmethod
    def fetch_from_api(cls, code_list: List[str]) -> Dict[str, RealtimePriceData]:
        """从 API 获取股票价格"""
        if not code_list:
            return {}
        
        try:
            url = STOCK_PRICE_API_URL + ','.join(code_list) + ','
            response = urllib.request.urlopen(url, timeout=10).read()
            response_array = str(response, encoding=ENCODING_GB18030).split(';')
            
            result = {}
            for index, single_response in enumerate(response_array):
                if index >= len(code_list) or len(single_response) <= MIN_RESPONSE_LENGTH:
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
                
                result[code_list[index]] = RealtimePriceData(
                    name=stock_info[1],
                    currentPrice=current_price,
                    priceOffset=price_offset,
                    offsetRatio=cls._calculate_offset_ratio(price_offset, yesterday_close),
                    yesterdayClose=yesterday_close
                )
            
            return result
        except Exception as e:
            logger.error(f"获取股票价格失败: {e}")
            return {}
