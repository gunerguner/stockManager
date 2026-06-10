"""百度股市通估值数据（港股 TTM PE、PB）"""
from ...common import logger
from .http_client import get_json

_BAIDU_URL = "https://gushitong.baidu.com/opendata"


def _baidu_indicator(
    code: str,
    market: str,
    indicator: str,
    *,
    timeout: int = 10,
) -> float | None:
    """返回该指标最新一日的值；失败返回 None。"""
    params = {
        "openapi": "1",
        "dspName": "iphone",
        "tn": "tangram",
        "client": "app",
        "query": indicator,
        "code": code,
        "word": "",
        "resource_id": "51171",
        "market": market,
        "tag": indicator,
        "chart_select": "近一年",
        "industry_select": "",
        "skip_industry": "1",
        "finClientType": "pc",
    }
    try:
        body = (
            get_json(_BAIDU_URL, params=params, timeout=timeout)["Result"][0]["DisplayData"][
                "resultData"
            ]["tplData"]["result"]["chartInfo"][0]["body"]
        )
        return float(body[-1][1]) if body else None
    except Exception as e:
        logger.error(f"百度估值获取失败 {market}:{code} {indicator}: {e}")
        return None


def fetch_pe_pb(code: str, market: str, *, timeout: int = 10) -> tuple[float | None, float | None]:
    """market: 'hk'(港股); code 已去前缀。返回 (peTtm, pb)。"""
    return (
        _baidu_indicator(code, market, "市盈率(TTM)", timeout=timeout),
        _baidu_indicator(code, market, "市净率", timeout=timeout),
    )
