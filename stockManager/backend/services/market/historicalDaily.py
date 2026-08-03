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
from backend.services.market.http_client import get_json

_CN_KLINE_URL = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get"
_HK_KLINE_URL = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/hkfqkline/get"
_CLOSE_INDEX = 2
_PERIOD = "day"
_CHUNK_DAYS = 300
_COUNT = 320
_MAX_RETRIES = 2
_RETRY_SLEEP_SEC = 0.4


def _parse_closes_from_node(node: dict) -> dict[date, float]:
    """从 K 线节点提取收盘价：优先不复权 day，过滤负价/零价。"""
    rows: list = []
    for key in ("day", "qfqday"):
        if isinstance(value := node.get(key), list) and value and isinstance(value[0], list):
            rows = value
            break
    else:
        for value in node.values():
            if isinstance(value, list) and value and isinstance(value[0], list):
                rows = value
                break

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
    url: str,
    start: date,
    end: date,
    *,
    timeout: int,
) -> dict[date, float]:
    # A 股：末段空 = 不复权；港股 hkfqkline 空参会 bad params，用 qfq 但优先解析 day
    adjust = "qfq" if is_hk_code(code) else ""
    param = (
        f"{code},{_PERIOD},{start.isoformat()},{end.isoformat()},{_COUNT},{adjust}"
    )
    last_error: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            data = get_json(url, params={"param": param}, timeout=timeout)
            api_code = data.get("code")
            if api_code not in (0, "0", None) and not data.get("data"):
                raise RuntimeError(f"gtimg code={api_code} msg={data.get('msg')}")
            payload = data.get("data") or {}
            if not payload:
                return {}
            node = next(iter(payload.values()))
            if not isinstance(node, dict):
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
    url = _HK_KLINE_URL if is_hk_code(code) else _CN_KLINE_URL
    merged: dict[date, float] = {}
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=_CHUNK_DAYS - 1), end)
        chunk = _fetch_chunk(code, url, cursor, chunk_end, timeout=timeout)
        merged.update(chunk)
        cursor = chunk_end + timedelta(days=1)
    return {d: px for d, px in merged.items() if start <= d <= end}
