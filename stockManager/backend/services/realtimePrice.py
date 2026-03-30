"""股票实时价格查询服务模块"""
from typing import List

from ..common import logger
from ..common.types import RealtimePriceData, RealtimePriceDict
from .cacheRepository import CacheRepository

# 懒加载 easyquotation 实例
_tencent_quotation = None


def _get_tencent_quotation():
    """获取腾讯行情实例（懒加载）"""
    global _tencent_quotation
    if _tencent_quotation is None:
        from easyquotation import use as eq_use
        _tencent_quotation = eq_use('tencent')
    return _tencent_quotation


class RealtimePrice:
    """股票实时价格查询服务"""

    @classmethod
    def _calculate_offset_ratio(cls, offset: float, base_price: float) -> str:
        if base_price == 0.0:
            return "0"
        return f"{(offset / base_price) * 100:.2f}%"

    @classmethod
    def query(cls, code_list: List[str]) -> RealtimePriceDict:
        """查询股票实时价格"""
        if not code_list:
            return {}

        cached_data, missing_codes = CacheRepository.get_stock_prices_with_cache(code_list)
        result = {code: RealtimePriceData(data) for code, data in cached_data.items()}

        if missing_codes:
            api_result = cls.fetch_from_api(missing_codes)
            if api_result:
                CacheRepository.set_stock_prices_batch(api_result)
                result.update(api_result)

        return result

    @classmethod
    def fetch_from_api(cls, code_list: List[str]) -> RealtimePriceDict:
        """从 API 获取股票价格（使用 easyquotation）"""
        if not code_list:
            return {}

        try:
            tencent = _get_tencent_quotation()
            # 使用 prefix=True 使返回的 key 也带前缀（如 sh600519）
            raw_data = tencent.real(code_list, prefix=True)

            result = {}
            for code, stock_data in raw_data.items():
                current_price = stock_data.get('now', 0.0)
                yesterday_close = stock_data.get('close', 0.0)
                price_offset = current_price - yesterday_close

                result[code] = RealtimePriceData({
                    "name": stock_data.get('name', ''),
                    "currentPrice": current_price,
                    "priceOffset": price_offset,
                    "offsetRatio": cls._calculate_offset_ratio(price_offset, yesterday_close),
                    "yesterdayClose": yesterday_close
                })

            return result
        except Exception as e:
            logger.error(f"获取股票价格失败: {e}")
            return {}
