"""股票实时价格外部数据源（A 股 easyquotation tencent；港股直连腾讯 sqt）"""
import re
from typing import Protocol, cast

from easyquotation import use as eq_use

from backend.common import logger
from backend.common.domain.market import hk_api_code, split_codes_by_market
from backend.common.types import RealtimePriceData, RealtimePriceDict
from backend.common.utils import safe_float
from backend.datasource.http_client import get_text

HK_QUOTE_URL = "http://sqt.gtimg.cn/utf8/q="
_HK_QUOTE_RE = re.compile(r'v_r_hk(\d+)="(.*?)"')
_HK_NAME_IDX = 1
_HK_PRICE_IDX = 3
_HK_CLOSE_IDX = 4


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


def _parse_hk_quote(payload: str) -> RealtimePriceData | None:
    """只取名称/现价/昨收。腾讯港股均价等字段常为空，不能整行 float。"""
    fields = payload.split("~")
    if len(fields) <= _HK_CLOSE_IDX:
        return None
    price_raw = fields[_HK_PRICE_IDX]
    close_raw = fields[_HK_CLOSE_IDX]
    if not price_raw or not close_raw:
        return None
    return _build_price(
        {
            "name": fields[_HK_NAME_IDX],
            "price": safe_float(price_raw),
            "lastPrice": safe_float(close_raw),
        },
        "price",
        "lastPrice",
    )


def _fetch_hk(code_list: list[str]) -> RealtimePriceDict:
    try:
        params = ",".join(f"r_hk{hk_api_code(code)}" for code in code_list)
        text = get_text(HK_QUOTE_URL + params)
    except Exception as e:
        logger.error(f"获取港股价格失败: {e}")
        return {}

    parsed: dict[str, RealtimePriceData] = {}
    for match in _HK_QUOTE_RE.finditer(text):
        api_code, payload = match.group(1), match.group(2)
        data = _parse_hk_quote(payload)
        if data is None:
            logger.warning(f"港股 {api_code} 行情字段无效，已跳过")
            continue
        parsed[api_code] = data

    result: RealtimePriceDict = {}
    for code in code_list:
        data = parsed.get(hk_api_code(code))
        if data:
            result[code] = data
    return result
