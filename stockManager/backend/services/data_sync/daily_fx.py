"""HKD/CNY 日频汇率持久化与缺口补拉（中行历史牌价）"""
from datetime import date, timedelta

from django.db import transaction

from backend.common import logger
from backend.common.domain.calendar import TradingCalendar
from backend.common.domain.market import Market
from backend.common.types import DailyFxSeries
from backend.datasource.exchangeRate import fetch_hkd_cny_daily_rates
from backend.models import HkdCnyDailyRate
from backend.services.data_sync.gaps import missing_session_gaps

_GAP_FILL_ROUNDS = 2
_SEED_LOOKBACK_DAYS = 30


def _load_rates(start: date, end: date) -> DailyFxSeries:
    """读取 [start, end] 内已有日频汇率。"""
    if start > end:
        return {}
    rows = HkdCnyDailyRate.objects.filter(date__gte=start, date__lte=end).values_list(
        "date", "close"
    )
    return {d: float(close) for d, close in rows}


def _load_latest_before(day: date) -> tuple[date, float] | None:
    """区间起点之前最近一条有效汇率，供向前填充。"""
    row = (
        HkdCnyDailyRate.objects.filter(date__lt=day, close__gt=0)
        .order_by("-date")
        .values_list("date", "close")
        .first()
    )
    if row is None:
        return None
    return row[0], float(row[1])


def _upsert_rates(rates: DailyFxSeries) -> None:
    if not rates:
        return
    objs = [
        HkdCnyDailyRate(date=d, close=str(rate))
        for d, rate in rates.items()
        if rate > 0
    ]
    if not objs:
        return
    with transaction.atomic():
        HkdCnyDailyRate.objects.bulk_create(
            objs,
            update_conflicts=True,
            unique_fields=["date"],
            update_fields=["close"],
        )


def _fetch_and_upsert_gaps(gaps: list[tuple[date, date]]) -> DailyFxSeries:
    fetched_all: DailyFxSeries = {}
    for gap_start, gap_end in gaps:
        try:
            fetched = fetch_hkd_cny_daily_rates(gap_start, gap_end)
        except Exception as exc:
            logger.warning(f"[daily_fx] 缺口 {gap_start}~{gap_end} 拉取失败: {exc}")
            continue
        if not fetched:
            logger.warning(f"[daily_fx] 缺口 {gap_start}~{gap_end} 为空")
            continue
        fetched_all.update(fetched)
    if fetched_all:
        _upsert_rates(fetched_all)
    return fetched_all


def ensure_hkd_cny_rates(start: date, end: date) -> DailyFxSeries:
    """确保 [start, end] 的 CN 交易日有日频汇率；并带回起点前最近一条作为种子。"""
    if start > end:
        return {}

    seed_start = start - timedelta(days=_SEED_LOOKBACK_DAYS)
    existing = _load_rates(seed_start, end)
    if _load_latest_before(seed_start) is None and not existing:
        try:
            seeded = fetch_hkd_cny_daily_rates(seed_start, start)
            if seeded:
                _upsert_rates(seeded)
                existing.update(seeded)
        except Exception as exc:
            logger.warning(f"[daily_fx] 起点前种子 {seed_start}~{start} 拉取失败: {exc}")

    for round_idx in range(_GAP_FILL_ROUNDS):
        if not (gaps := missing_session_gaps(existing, start, end, Market.CN)):
            break
        logger.info(
            f"[daily_fx] 第 {round_idx + 1} 轮补拉 {len(gaps)} 个缺口: "
            + ", ".join(f"{a}~{b}" for a, b in gaps[:8])
            + (" ..." if len(gaps) > 8 else "")
        )
        existing.update(_fetch_and_upsert_gaps(gaps))
    else:
        remain = missing_session_gaps(existing, start, end, Market.CN)
        if remain:
            miss_days = sum(
                len(TradingCalendar.sessions_between(a, b, Market.CN))
                for a, b in remain
            )
            logger.warning(
                f"[daily_fx] 仍缺约 {miss_days} 个交易日 "
                f"({remain[0][0]}~{remain[-1][1]})"
            )

    if (seed := _load_latest_before(start)) is not None:
        existing.setdefault(seed[0], seed[1])
    return existing
