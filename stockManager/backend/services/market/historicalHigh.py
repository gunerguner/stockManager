"""近 6 年历史最高价（腾讯 gtimg 周线）

返回的 K 线行格式为 [日期, 开, 收, 高, 低, 量]，最高价位于索引 3。
- 港股：前复权（qfq），港币，走专用 endpoint `hkfqkline/get`（`fqkline/get` 对港股 qfq 静默忽略）
- A 股：前复权（qfq），对齐原 baostock adjustflag=2 口径
"""
from datetime import datetime, timedelta

from backend.common import logger
from backend.services.market.http_client import get_json

_CN_KLINE_URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
_HK_KLINE_URL = "https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get"
_MONTHS = 72  # 6 年
_HIGH_INDEX = 3
_PERIOD = "week"
_COUNT = 400


def _date_range() -> tuple[str, str]:
    end = datetime.today()
    start = end - timedelta(days=_MONTHS * 31)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _extract_kline(node: dict) -> list[list]:
    """从返回节点中找出 K 线数组（week / qfqweek 等键名随复权方式变化）。"""
    for value in node.values():
        if isinstance(value, list) and value and isinstance(value[0], list):
            return value
    return []


def _fetch_gtimg_hist_high(code: str, url: str, *, timeout: int) -> float | None:
    """通用 gtimg 6 年周线前复权最高价；code 为 gtimg 代码（hkXXXXX / shXXXXXX / szXXXXXX）。"""
    start_str, end_str = _date_range()
    param = f"{code},{_PERIOD},{start_str},{end_str},{_COUNT},qfq"
    try:
        data = get_json(url, params={"param": param}, timeout=timeout)
        payload = data.get("data") or {}
        if not payload:
            return None
        node = next(iter(payload.values()))
        rows = _extract_kline(node)
        highs = [float(row[_HIGH_INDEX]) for row in rows if len(row) > _HIGH_INDEX]
        return max(highs) if highs else None
    except Exception as e:
        logger.error(f"[historicalHigh] 获取 {code} 6年高失败: {e}")
        return None


def fetch_hk_hist_high(code: str, *, timeout: int = 10) -> float | None:
    """港股 hkXXXXX 近 6 年周线最高价（前复权，港币）；失败返回 None。"""
    return _fetch_gtimg_hist_high(code, _HK_KLINE_URL, timeout=timeout)


def fetch_cn_hist_high(code: str, *, timeout: int = 10) -> float | None:
    """A 股 shXXXXXX/szXXXXXX 近 6 年周线最高价（前复权）；失败返回 None。"""
    return _fetch_gtimg_hist_high(code, _CN_KLINE_URL, timeout=timeout)
