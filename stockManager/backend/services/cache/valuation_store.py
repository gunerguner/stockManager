"""每股估值指标缓存（epsTtm / bvps，价格无关）

A 股与港股统一走百度 opendata：A 股 market=ab，港股 market=hk。
base_close 取实时行情的 yesterdayClose，epsTtm=close/peTTM、bvps=close/pbMRQ。
"""
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.cache import cache

from ...common.cache import Cache
from ...common import logger
from ...common.market import to_baidu_params
from ...common.types import RealtimePriceDict, ValuationData
from ..market import fetch_pe_pb
from . import keys

_VALUATION_TIMEOUT = 5
_MAX_WORKERS = 8


def _valuation_from_pe_pb(
    base_close: float | None,
    pe_ttm: float | None,
    pb: float | None,
) -> ValuationData:
    eps_ttm: float | None = None
    bvps: float | None = None
    if base_close and pe_ttm and pe_ttm != 0:
        eps_ttm = base_close / pe_ttm
    if base_close and pb and pb != 0:
        bvps = base_close / pb
    return ValuationData(epsTtm=eps_ttm, bvps=bvps)


def _cache_valuation(code: str, entry: ValuationData) -> None:
    cache.set(keys.KEY_VALUATION.format(code=code), entry, keys.TTL_VALUATION)


def get_cached_valuations(codes: list[str]) -> tuple[dict[str, ValuationData], list[str]]:
    """批量读缓存，返回 (已命中, 未命中 code 列表)。"""
    result: dict[str, ValuationData] = {}
    missing: list[str] = []
    if not codes:
        return result, missing

    cache_keys = [keys.KEY_VALUATION.format(code=code) for code in codes]
    batch = Cache.get_many(cache_keys)
    for code, cache_key in zip(codes, cache_keys, strict=False):
        cached = batch.get(cache_key)
        if cached is not None:
            result[code] = cached
        else:
            missing.append(code)
    return result, missing


def _fetch_single_valuation(code: str, price_map: RealtimePriceDict) -> tuple[str, ValuationData]:
    try:
        baidu = to_baidu_params(code)
        price_data = price_map.get(code) or {}
        base_close = price_data.get("yesterdayClose")
        entry = ValuationData(epsTtm=None, bvps=None)
        if baidu and base_close:
            market, pure_code = baidu
            pe_ttm, pb = fetch_pe_pb(pure_code, market, timeout=_VALUATION_TIMEOUT)
            entry = _valuation_from_pe_pb(base_close, pe_ttm, pb)
    except Exception as e:
        logger.warning(f"估值拉取失败 {code}: {e}")
        entry = ValuationData(epsTtm=None, bvps=None)
    _cache_valuation(code, entry)
    return code, entry


def fetch_and_cache_valuations(
    codes: list[str],
    price_map: RealtimePriceDict,
) -> dict[str, ValuationData]:
    """有界并发拉取估值并写缓存（A 股与港股统一走百度）。"""
    if not codes:
        return {}

    result: dict[str, ValuationData] = {}
    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = [
            executor.submit(_fetch_single_valuation, code, price_map)
            for code in codes
        ]
        for future in as_completed(futures):
            code, entry = future.result()
            result[code] = entry
    return result
