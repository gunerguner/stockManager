"""净值展示摊入与区间指标（纯函数）"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta

from backend.common.types import (
    NavAnalysisResult,
    NavDrawdownPeriod,
    NavMaxNavMarker,
    NavMetricsByRange,
    NavMetricsData,
    NavPointData,
)

_TRADING_DAYS_PER_YEAR = 242
_MIN_STD = 1e-12


def apply_income_cash_display(
    points: list[tuple[date, float]],
    income_cash: float,
    origin_cash: float,
) -> list[NavPointData]:
    """库内 nav + incomeCash 线性摊入 → navDisplay。"""
    n = len(points)
    if not n:
        return []
    denom = origin_cash if abs(origin_cash) > 1e-6 else 1.0
    daily_adj = (income_cash / denom) / n if abs(income_cash) > 1e-9 else 0.0
    result: list[NavPointData] = []
    for i, (d, nav) in enumerate(points):
        result.append({
            'date': d.isoformat(),
            'nav': nav,
            'navDisplay': nav + daily_adj * (i + 1),
        })
    return result


def _daily_returns(navs: list[float]) -> list[float]:
    rets: list[float] = []
    for i in range(1, len(navs)):
        prev = navs[i - 1]
        if abs(prev) < 1e-12:
            continue
        rets.append(navs[i] / prev - 1.0)
    return rets


def _empty_metrics() -> NavMetricsData:
    return {
        'annualizedReturn': 0.0,
        'sharpeRatio': 0.0,
        'maxDrawdown': 0.0,
        'calmarRatio': 0.0,
        'maxNav': None,
        'drawdown': None,
    }


def _build_drawdown_period(
    points: list[NavPointData],
    navs: list[float],
    dd_peak_idx: int,
    trough_idx: int,
) -> NavDrawdownPeriod:
    peak_date = points[dd_peak_idx]['date']
    trough_date = points[trough_idx]['date']
    peak_nav = navs[dd_peak_idx]
    recovery_idx: int | None = None
    for i in range(trough_idx + 1, len(navs)):
        if navs[i] >= peak_nav:
            recovery_idx = i
            break
    if recovery_idx is not None:
        end_date = points[recovery_idx]['date']
        trough_d = datetime.strptime(trough_date, '%Y-%m-%d').date()
        recover_d = datetime.strptime(end_date, '%Y-%m-%d').date()
        return {
            'peakDate': peak_date,
            'troughDate': trough_date,
            'endDate': end_date,
            'recovered': True,
            'recoverDays': (recover_d - trough_d).days,
        }
    return {
        'peakDate': peak_date,
        'troughDate': trough_date,
        'endDate': points[-1]['date'],
        'recovered': False,
        'recoverDays': None,
    }


def compute_metrics(points: list[NavPointData]) -> NavMetricsData:
    """基于展示净值序列计算年化 / 夏普 / 最大回撤 / 卡玛（rf=0）及图表锚点。"""
    empty = _empty_metrics()
    if not points:
        return empty

    max_nav_idx = 0
    for i in range(1, len(points)):
        if points[i]['navDisplay'] > points[max_nav_idx]['navDisplay']:
            max_nav_idx = i
    max_nav: NavMaxNavMarker = {
        'date': points[max_nav_idx]['date'],
        'display': points[max_nav_idx]['navDisplay'],
    }
    empty['maxNav'] = max_nav

    if len(points) < 2:
        return empty

    navs = [p['navDisplay'] for p in points]
    start, end = navs[0], navs[-1]
    days = len(navs) - 1
    if start <= 0 or days <= 0:
        return empty

    annualized = (end / start) ** (_TRADING_DAYS_PER_YEAR / days) - 1.0

    rets = _daily_returns(navs)
    sharpe = 0.0
    if len(rets) >= 2:
        mean = sum(rets) / len(rets)
        var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
        std = math.sqrt(var)
        if std > _MIN_STD:
            sharpe = (mean / std) * math.sqrt(_TRADING_DAYS_PER_YEAR)

    running_peak = navs[0]
    running_peak_idx = 0
    max_dd = 0.0
    dd_peak_idx = 0
    trough_idx = 0
    for i, v in enumerate(navs):
        if v > running_peak:
            running_peak = v
            running_peak_idx = i
        if running_peak > 0:
            dd = v / running_peak - 1.0
            if dd < max_dd:
                max_dd = dd
                dd_peak_idx = running_peak_idx
                trough_idx = i

    calmar = 0.0
    if abs(max_dd) > 1e-12:
        calmar = annualized / abs(max_dd)

    drawdown: NavDrawdownPeriod | None = None
    if abs(max_dd) > 1e-12:
        drawdown = _build_drawdown_period(points, navs, dd_peak_idx, trough_idx)

    return {
        'annualizedReturn': annualized,
        'sharpeRatio': sharpe,
        'maxDrawdown': max_dd,
        'calmarRatio': calmar,
        'maxNav': max_nav,
        'drawdown': drawdown,
    }


def _slice_by_range(points: list[NavPointData], range_key: str) -> list[NavPointData]:
    if not points or range_key == 'all':
        return points
    today = date.today()
    if range_key == 'ytd':
        start = date(today.year, 1, 1)
    elif range_key == 'oneYear':
        start = today - timedelta(days=365)
    else:
        return points
    return [p for p in points if datetime.strptime(p['date'], '%Y-%m-%d').date() >= start]


def compute_metrics_by_range(points: list[NavPointData]) -> NavMetricsByRange:
    """按 all / ytd / oneYear 切片计算指标。"""
    return {
        'all': compute_metrics(points),
        'ytd': compute_metrics(_slice_by_range(points, 'ytd')),
        'oneYear': compute_metrics(_slice_by_range(points, 'oneYear')),
    }


def assemble_nav_analysis(
    db_points: list[tuple[date, float]],
    income_cash: float,
    origin_cash: float,
    *,
    updated_at: str | None = None,
) -> NavAnalysisResult:
    """组装 API / Redis 缓存 payload。"""
    points = apply_income_cash_display(db_points, income_cash, origin_cash)
    last_date = points[-1]['date'] if points else None
    result: NavAnalysisResult = {
        'points': points,
        'metrics': compute_metrics_by_range(points),
        'incomeCash': income_cash,
        'originCash': origin_cash,
        'lastDate': last_date,
        'updatedAt': updated_at,
    }
    return result
