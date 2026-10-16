"""净值图基准指数：元数据、补拉窗口与收盘对齐（纯函数）"""
from datetime import date
from typing import NamedTuple, cast

from backend.common.types import (
    DailyCloseByCode,
    HoldingWindows,
    NavBenchmarkCloses,
    NavBenchmarkMeta,
)


class BenchmarkSpec(NamedTuple):
    key: str
    code: str
    name: str
    available_from: date


# 价格指数。available_from 为行情发布日，上市前不补拉、不对齐成 0。
BENCHMARKS: tuple[BenchmarkSpec, ...] = (
    BenchmarkSpec('hs300', 'sh000300', '沪深300', date(2005, 4, 8)),
    BenchmarkSpec('cyb', 'sz399006', '创业板指', date(2010, 6, 1)),
    BenchmarkSpec('kc50', 'sh000688', '科创50', date(2020, 7, 23)),
)


def empty_benchmark_closes() -> NavBenchmarkCloses:
    return {'hs300': None, 'cyb': None, 'kc50': None}


def benchmark_metas() -> list[NavBenchmarkMeta]:
    return [
        {
            'key': spec.key,
            'code': spec.code,
            'name': spec.name,
            'availableFrom': spec.available_from.isoformat(),
        }
        for spec in BENCHMARKS
    ]


def benchmark_windows(start: date, end: date) -> HoldingWindows:
    """每条指数一个窗口，起点不早于发布日。"""
    if start > end:
        return {}
    windows: HoldingWindows = {}
    for spec in BENCHMARKS:
        win_start = max(start, spec.available_from)
        if win_start <= end:
            windows[spec.code] = [(win_start, end)]
    return windows


def align_benchmark_closes(
    dates: list[date],
    closes_by_code: DailyCloseByCode,
) -> list[NavBenchmarkCloses]:
    """按净值日对齐收盘。当天没有收盘为 None，不向前填充。"""
    aligned: list[NavBenchmarkCloses] = []
    for day in dates:
        raw = dict(empty_benchmark_closes())
        for spec in BENCHMARKS:
            close = (closes_by_code.get(spec.code) or {}).get(day)
            if close is not None and close > 0:
                raw[spec.key] = float(close)
        aligned.append(cast(NavBenchmarkCloses, raw))
    return aligned


def nav_cache_has_benchmarks(result: object) -> bool:
    """旧缓存没有 benchmarks 字段时视为未命中。"""
    return isinstance(result, dict) and 'benchmarks' in result
