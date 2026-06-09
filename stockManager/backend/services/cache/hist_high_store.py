"""近 6 年历史最高价缓存"""
from django.core.cache import cache

from ...common.market import split_codes_by_market
from ..market import fetch_cn_hist_highs, fetch_hk_hist_high
from . import keys

_SENTINEL_NONE = "__none__"


def _cache_hist_high(code: str, value: float | None) -> None:
    cache.set(
        keys.KEY_HIST_HIGH.format(code=code),
        value if value is not None else _SENTINEL_NONE,
        keys.TTL_HIST_HIGH,
    )


def get_hist_highs(codes: list[str]) -> dict[str, float | None]:
    """返回 {code: histHigh}；A 股走 baostock，港股走 gtimg。"""
    result: dict[str, float | None] = {}
    missing: list[str] = []

    for code in codes:
        cached = cache.get(keys.KEY_HIST_HIGH.format(code=code))
        if cached is not None:
            result[code] = None if cached == _SENTINEL_NONE else cached
        else:
            missing.append(code)

    if not missing:
        return result

    cn_missing, hk_missing = split_codes_by_market(missing)

    if cn_missing:
        cn_highs = fetch_cn_hist_highs(cn_missing)
        for code in cn_missing:
            value = cn_highs.get(code)
            _cache_hist_high(code, value)
            result[code] = value

    for code in hk_missing:
        value = fetch_hk_hist_high(code)
        _cache_hist_high(code, value)
        result[code] = value

    return result
