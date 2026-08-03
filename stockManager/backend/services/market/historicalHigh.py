"""近 6 年历史最高价（腾讯 gtimg 周线）

返回的 K 线行格式为 [日期, 开, 收, 高, 低, 量]，最高价位于索引 3。
- 港股：前复权（qfq），港币，走专用 endpoint `hkfqkline/get`
- A 股：前复权（qfq），对齐原 baostock adjustflag=2 口径
"""
from datetime import datetime, timedelta

from backend.common import logger
from backend.services.market.gtimg_kline import (
    extract_kline_rows,
    fetch_kline_node,
    kline_url_for_code,
)

_MONTHS = 72  # 6 年
_HIGH_INDEX = 3
_PERIOD = "week"
_COUNT = 400
_PREFERRED_KEYS = ("qfqweek", "week", "qfqday", "day")


def _date_range() -> tuple[str, str]:
    end = datetime.today()
    start = end - timedelta(days=_MONTHS * 31)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def fetch_hist_high(code: str, *, timeout: int = 10) -> float | None:
    """近 6 年周线最高价（前复权）；港股为港币。失败返回 None。"""
    start_str, end_str = _date_range()
    try:
        if (node := fetch_kline_node(
            code,
            period=_PERIOD,
            start=start_str,
            end=end_str,
            count=_COUNT,
            adjust="qfq",
            timeout=timeout,
            url=kline_url_for_code(code),
        )) is None:
            return None
        rows = extract_kline_rows(node, _PREFERRED_KEYS)
        if not (highs := [float(row[_HIGH_INDEX]) for row in rows if len(row) > _HIGH_INDEX]):
            return None
        return max(highs)
    except Exception as e:
        logger.error(f"[historicalHigh] 获取 {code} 6年高失败: {e}")
        return None
