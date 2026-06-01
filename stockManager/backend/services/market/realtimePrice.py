"""股票实时价格查询服务模块"""

from easyquotation import use as eq_use

from ...common import logger
from ...common.types import RealtimePriceData, RealtimePriceDict
from ...common.utils import format_percent
from ..cache import CacheRepository
from .stockNameSync import StockNameSync

_tencent_quotation = None
_hk_quotation = None


def _get_tencent_quotation():
    """获取腾讯 A 股行情实例（懒加载）"""
    global _tencent_quotation
    if _tencent_quotation is None:
        _tencent_quotation = eq_use('tencent')
    return _tencent_quotation


def _get_hk_quotation():
    """获取腾讯港股行情实例（懒加载）"""
    global _hk_quotation
    if _hk_quotation is None:
        _hk_quotation = eq_use('hkquote')
    return _hk_quotation


def _build_cn_realtime_price(stock_data: dict) -> RealtimePriceData:
    current_price = float(stock_data.get('now', 0.0) or 0.0)
    yesterday_close = float(stock_data.get('close', 0.0) or 0.0)
    price_offset = current_price - yesterday_close
    return RealtimePriceData({
        "name": stock_data.get('name', ''),
        "currentPrice": current_price,
        "priceOffset": price_offset,
        "offsetRatio": format_percent(price_offset / yesterday_close) if yesterday_close != 0 else "0%",
        "yesterdayClose": yesterday_close,
    })


def _build_hk_realtime_price(stock_data: dict) -> RealtimePriceData:
    current_price = float(stock_data.get('price', 0.0) or 0.0)
    yesterday_close = float(stock_data.get('lastPrice', 0.0) or 0.0)
    price_offset = current_price - yesterday_close
    return RealtimePriceData({
        "name": stock_data.get('name', ''),
        "currentPrice": current_price,
        "priceOffset": price_offset,
        "offsetRatio": format_percent(price_offset / yesterday_close) if yesterday_close != 0 else "0%",
        "yesterdayClose": yesterday_close,
    })


_REQUIRED_CACHE_FIELDS = frozenset({
    "name", "currentPrice", "priceOffset", "offsetRatio", "yesterdayClose",
})


def _is_valid_cached_price(data: dict | None) -> bool:
    return bool(data) and _REQUIRED_CACHE_FIELDS.issubset(data.keys())


class RealtimePrice:
    """股票实时价格查询服务"""

    @classmethod
    def query(cls, code_list: list[str]) -> RealtimePriceDict:
        """查询股票实时价格"""
        if not code_list:
            return {}

        cached_data, missing_codes = CacheRepository.get_stock_prices_with_cache(code_list)
        result: RealtimePriceDict = {}
        for code, data in cached_data.items():
            if _is_valid_cached_price(data):
                result[code] = RealtimePriceData(data)
            else:
                missing_codes.append(code)

        if missing_codes:
            api_result = cls.fetch_from_api(missing_codes)
            if api_result:
                CacheRepository.set_stock_prices_batch(api_result)
                result.update(api_result)

        return result

    @classmethod
    def fetch_from_api(cls, code_list: list[str], sync_names: bool = True) -> RealtimePriceDict:
        """从 API 获取股票价格（A 股 tencent + 港股 hkquote）"""
        if not code_list:
            return {}

        cn_codes = [c for c in code_list if not c.lower().startswith('hk')]
        hk_codes = [c for c in code_list if c.lower().startswith('hk')]
        result: RealtimePriceDict = {}

        if cn_codes:
            result.update(cls._fetch_cn(cn_codes))
        if hk_codes:
            result.update(cls._fetch_hk(hk_codes))

        if sync_names and result:
            StockNameSync.sync_from_realtime(result)
        return result

    @classmethod
    def _fetch_cn(cls, code_list: list[str]) -> RealtimePriceDict:
        try:
            tencent = _get_tencent_quotation()
            raw_data = tencent.real(code_list, prefix=True)
            return {
                code: _build_cn_realtime_price(stock_data)
                for code, stock_data in raw_data.items()
            }
        except Exception as e:
            logger.error(f"获取 A 股价格失败: {e}")
            return {}

    @classmethod
    def _fetch_hk(cls, code_list: list[str]) -> RealtimePriceDict:
        try:
            hkquote = _get_hk_quotation()
            # hk00700 -> 00700
            api_codes = [c[2:] if c.lower().startswith('hk') else c for c in code_list]
            raw_data = hkquote.real(api_codes)
            result: RealtimePriceDict = {}
            for code in code_list:
                api_code = code[2:] if code.lower().startswith('hk') else code
                stock_data = raw_data.get(api_code)
                if stock_data:
                    result[code] = _build_hk_realtime_price(stock_data)
            return result
        except Exception as e:
            logger.error(f"获取港股价格失败: {e}")
            return {}
