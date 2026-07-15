"""股票实时价格外部数据源（easyquotation tencent / hkquote）"""
from typing import Protocol, cast

from easyquotation import use as eq_use

from backend.common import logger
from backend.common.market import hk_api_code, split_codes_by_market
from backend.common.types import RealtimePriceData, RealtimePriceDict
from backend.common.utils import safe_float


class _EasyQuotation(Protocol):
    def real(self, code_list: list[str], prefix: bool = False) -> dict[str, dict]: ...


_quotations: dict[str, _EasyQuotation] = {}


def _quotation(name: str) -> _EasyQuotation:
    if name not in _quotations:
        _quotations[name] = cast(_EasyQuotation, eq_use(name))
    return _quotations[name]


def _build_price(stock_data: dict, price_key: str, close_key: str) -> RealtimePriceData:
    current = float(stock_data.get(price_key, 0.0) or 0.0)
    close = float(stock_data.get(close_key, 0.0) or 0.0)
    offset = current - close
    return RealtimePriceData({
        "name": stock_data.get("name", ""),
        "currentPrice": current,
        "priceOffset": offset,
        "offsetRatio": offset / close if close else 0.0,
        "yesterdayClose": close,
        "yearHigh": None,
    })


def _build_price_cn(stock_data: dict, price_key: str, close_key: str) -> RealtimePriceData:
    base = _build_price(stock_data, price_key, close_key)
    high_raw = stock_data.get("high_2")
    base["yearHigh"] = safe_float(high_raw) if high_raw else None
    return base


def _build_price_hk(stock_data: dict, price_key: str, close_key: str) -> RealtimePriceData:
    base = _build_price(stock_data, price_key, close_key)
    high_raw = stock_data.get("year_high")
    base["yearHigh"] = safe_float(high_raw) if high_raw else None
    return base


def fetch_prices(code_list: list[str]) -> RealtimePriceDict:
    if not code_list:
        return {}
    cn_codes, hk_codes = split_codes_by_market(code_list)
    result: RealtimePriceDict = {}
    if cn_codes:
        result.update(_fetch_cn(cn_codes))
    if hk_codes:
        result.update(_fetch_hk(hk_codes))
    return result


def _fetch_cn(code_list: list[str]) -> RealtimePriceDict:
    try:
        return {
            code: _build_price_cn(data, "now", "close")
            for code, data in _quotation("tencent").real(code_list, prefix=True).items()
        }
    except Exception as e:
        logger.error(f"获取 A 股价格失败: {e}")
        return {}


def _fetch_hk(code_list: list[str]) -> RealtimePriceDict:
    try:
        raw = _quotation("hkquote").real([hk_api_code(code) for code in code_list])
        return {
            code: _build_price_hk(raw[hk_api_code(code)], "price", "lastPrice")
            for code in code_list
            if raw.get(hk_api_code(code))
        }
    except Exception as e:
        logger.error(f"获取港股价格失败: {e}")
        return {}
