"""港股近 6 年历史最高价（腾讯 gtimg 周线，不复权）

返回的 K 线行格式为 [日期, 开, 收, 高, 低, 量]，最高价位于索引 3。
A 股历史高由 baostock_source.fetch_cn_hist_high 承接。
"""
from datetime import datetime, timedelta

from ...common import logger
from .http_client import get_json

_KLINE_URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
_MONTHS = 72  # 6 年
_HIGH_INDEX = 3
_PERIOD = "week"
_COUNT = 400


def _date_range() -> tuple[str, str]:
    end = datetime.today()
    start = end - timedelta(days=_MONTHS * 31)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _extract_kline(node: dict) -> list[list]:
    """从返回节点中找出 K 线数组（day / week 等键名随复权方式变化）。"""
    for value in node.values():
        if isinstance(value, list) and value and isinstance(value[0], list):
            return value
    return []


def fetch_hk_hist_high(code: str) -> float | None:
    """港股 hkXXXXX 近 6 年周线最高价（不复权，港币）；失败返回 None。"""
    start_str, end_str = _date_range()
    param = f"{code},{_PERIOD},{start_str},{end_str},{_COUNT},bfq"
    try:
        data = get_json(_KLINE_URL, params={"param": param})
        payload = data.get("data") or {}
        if not payload:
            return None
        node = next(iter(payload.values()))
        rows = _extract_kline(node)
        highs = [float(row[_HIGH_INDEX]) for row in rows if len(row) > _HIGH_INDEX]
        return max(highs) if highs else None
    except Exception as e:
        logger.error(f"[historicalHigh] 获取港股 {code} 6年高失败: {e}")
        return None
