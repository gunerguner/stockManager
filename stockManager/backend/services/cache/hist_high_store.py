"""近 6 年历史最高价缓存（全部走腾讯 gtimg 周线：A 股 qfq / 港股 bfq）"""
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.cache import cache

from ...common.cache import Cache
from ...common import logger
from ...common.market import Market, code_to_market
from ..market import fetch_cn_hist_high, fetch_hk_hist_high
from . import keys

_SENTINEL_NONE = "__none__"
_HIST_HIGH_TIMEOUT = 5
_MAX_WORKERS = 8


def _cache_hist_high(code: str, value: float | None) -> None:
    cache.set(
        keys.KEY_HIST_HIGH.format(code=code),
        value if value is not None else _SENTINEL_NONE,
        keys.TTL_HIST_HIGH,
    )


def get_cached_hist_highs(codes: list[str]) -> tuple[dict[str, float | None], list[str]]:
    """批量读缓存，返回 (已命中, 未命中 code 列表)。"""
    result: dict[str, float | None] = {}
    missing: list[str] = []
    if not codes:
        return result, missing

    cache_keys = [keys.KEY_HIST_HIGH.format(code=code) for code in codes]
    batch = Cache.get_many(cache_keys)
    for code, cache_key in zip(codes, cache_keys, strict=False):
        cached = batch.get(cache_key)
        if cached is not None:
            result[code] = None if cached == _SENTINEL_NONE else cached
        else:
            missing.append(code)
    return result, missing


def _fetch_single_hist_high(code: str) -> tuple[str, float | None]:
    try:
        if code_to_market(code) == Market.HK:
            value = fetch_hk_hist_high(code, timeout=_HIST_HIGH_TIMEOUT)
        else:
            value = fetch_cn_hist_high(code, timeout=_HIST_HIGH_TIMEOUT)
    except Exception as e:
        logger.warning(f"历史高拉取失败 {code}: {e}")
        value = None
    _cache_hist_high(code, value)
    return code, value


def fetch_and_cache_hist_highs(codes: list[str]) -> dict[str, float | None]:
    """有界并发拉取历史高并写缓存（A 股与港股统一走 gtimg）。"""
    if not codes:
        return {}

    result: dict[str, float | None] = {}
    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = [executor.submit(_fetch_single_hist_high, code) for code in codes]
        for future in as_completed(futures):
            code, value = future.result()
            result[code] = value
    return result
