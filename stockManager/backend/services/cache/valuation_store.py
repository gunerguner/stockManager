"""每股估值指标缓存（epsTtm / bvps，价格无关）"""
from django.core.cache import cache

from ...common.market import split_codes_by_market, to_baidu_params
from ...common.types import RealtimePriceDict, ValuationData
from ..market import fetch_cn_valuation, fetch_pe_pb
from . import keys


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


def get_valuations(codes: list[str], price_map: RealtimePriceDict) -> dict[str, ValuationData]:
    """返回 {code: {epsTtm, bvps}}；A 股走 baostock，港股走百度。"""
    result: dict[str, ValuationData] = {}
    missing: list[str] = []
    for code in codes:
        cache_key = keys.KEY_VALUATION.format(code=code)
        cached = cache.get(cache_key)
        if cached is not None:
            result[code] = cached
        else:
            missing.append(code)

    if not missing:
        return result

    cn_missing, hk_missing = split_codes_by_market(missing)

    if cn_missing:
        cn_vals = fetch_cn_valuation(cn_missing)
        for code in cn_missing:
            row = cn_vals.get(code, {})
            price_data = price_map.get(code) or {}
            base_close = row.get("close") or price_data.get("yesterdayClose")
            entry = _valuation_from_pe_pb(
                base_close,
                row.get("peTTM"),
                row.get("pbMRQ"),
            )
            result[code] = entry
            _cache_valuation(code, entry)

    for code in hk_missing:
        baidu = to_baidu_params(code)
        price_data = price_map.get(code) or {}
        base_close = price_data.get("yesterdayClose")
        entry = ValuationData(epsTtm=None, bvps=None)
        if baidu and base_close:
            _, pure_code = baidu
            pe_ttm, pb = fetch_pe_pb(pure_code, "hk")
            entry = _valuation_from_pe_pb(base_close, pe_ttm, pb)
        result[code] = entry
        _cache_valuation(code, entry)

    return result
