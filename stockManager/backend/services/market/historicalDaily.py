"""日频不复权收盘价（腾讯 proxy.finance.qq.com）

K 线行格式：[日期, 开, 收, 高, 低, 量]，收盘价位于索引 2。

本项目已通过 Operation(DV) 回放持股，盯市必须用不复权价，
否则会与送转/除权重复折算。腾讯早期 qfqday 还存在负收盘等脏数据。

- A 股：newfqkline，取 day
- 港股：hkfqkline，取 day（不用 qfq）
"""
from datetime import date, datetime, timedelta
from time import sleep

from backend.common import logger
from backend.common.market import is_hk_code
from backend.services.market.gtimg_kline import (
    extract_kline_rows,
    fetch_kline_node,
    kline_url_for_code,
)

_CLOSE_INDEX = 2
_PERIOD = "day"
_CHUNK_DAYS = 300
_COUNT = 320
_MAX_RETRIES = 2
_RETRY_SLEEP_SEC = 0.4
_PREFERRED_KEYS = ("day", "qfqday")


def _parse_closes_from_node(node: dict) -> dict[date, float]:
    """从 K 线节点提取收盘价：优先不复权 day，过滤负价/零价。"""
    rows = extract_kline_rows(node, _PREFERRED_KEYS)
    result: dict[date, float] = {}
    for row in rows:
        if not isinstance(row, list) or len(row) <= _CLOSE_INDEX:
            continue
        try:
            d = datetime.strptime(str(row[0])[:10], "%Y-%m-%d").date()
            close = float(row[_CLOSE_INDEX])
        except (ValueError, TypeError):
            continue
        if close > 0:
            result[d] = close
    return result


def _fetch_chunk(
    code: str,
    start: date,
    end: date,
    *,
    timeout: int,
) -> dict[date, float]:
    # A 股：末段空 = 不复权；港股 hkfqkline 空参会 bad params，用 qfq 但优先解析 day
    adjust = "qfq" if is_hk_code(code) else ""
    last_error: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            if (node := fetch_kline_node(
                code,
                period=_PERIOD,
                start=start.isoformat(),
                end=end.isoformat(),
                count=_COUNT,
                adjust=adjust,
                timeout=timeout,
                url=kline_url_for_code(code),
            )) is None:
                return {}
            return _parse_closes_from_node(node)
        except Exception as e:
            last_error = e
            logger.warning(
                f"[historicalDaily] {code} {start}~{end} 第 {attempt}/{_MAX_RETRIES} 次失败: {e}"
            )
            if attempt < _MAX_RETRIES:
                sleep(_RETRY_SLEEP_SEC * attempt)
    logger.error(f"[historicalDaily] 获取 {code} {start}~{end} 最终失败: {last_error}")
    return {}


def fetch_daily_closes(
    code: str,
    start: date,
    end: date,
    *,
    timeout: int = 15,
) -> dict[date, float]:
    """拉取 [start, end] 日频不复权收盘价；失败或缺数据返回已拉到的子集。"""
    if start > end:
        return {}
    merged: dict[date, float] = {}
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=_CHUNK_DAYS - 1), end)
        chunk = _fetch_chunk(code, cursor, chunk_end, timeout=timeout)
        merged.update(chunk)
        cursor = chunk_end + timedelta(days=1)
    return {d: px for d, px in merged.items() if start <= d <= end}
