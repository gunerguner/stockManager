"""股票实时价格外部数据源（easyquotation tencent / hkquote）"""
from easyquotation import use as eq_use

from ...common import logger
from ...common.market import hk_api_code, split_codes_by_market
from ...common.types import RealtimePriceData, RealtimePriceDict
from ...common.utils import format_percent

_quotations: dict[str, object] = {}


def _quotation(name: str):
    if name not in _quotations:
        _quotations[name] = eq_use(name)
    return _quotations[name]


def _build_price(stock_data: dict, price_key: str, close_key: str) -> RealtimePriceData:
    current = float(stock_data.get(price_key, 0.0) or 0.0)
    close = float(stock_data.get(close_key, 0.0) or 0.0)
    offset = current - close
    return RealtimePriceData({
        "name": stock_data.get("name", ""),
        "currentPrice": current,
        "priceOffset": offset,
        "offsetRatio": format_percent(offset / close) if close else "0%",
        "yesterdayClose": close,
    })


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
            code: _build_price(data, "now", "close")
            for code, data in _quotation("tencent").real(code_list, prefix=True).items()
        }
    except Exception as e:
        logger.error(f"获取 A 股价格失败: {e}")
        return {}


def _fetch_hk(code_list: list[str]) -> RealtimePriceDict:
    try:
        raw = _quotation("hkquote").real([hk_api_code(code) for code in code_list])
        return {
            code: _build_price(raw[hk_api_code(code)], "price", "lastPrice")
            for code in code_list
            if raw.get(hk_api_code(code))
        }
    except Exception as e:
        logger.error(f"获取港股价格失败: {e}")
        return {}
