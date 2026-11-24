"""组合净值用例：刷新回放写库与展示指标组装"""
from datetime import date, datetime, timedelta, timezone

from django.contrib.auth.models import User
from django.db import transaction

from backend.common import logger
from backend.common.domain.calendar import TradingCalendar
from backend.common.domain.market import is_hk_code
from backend.common.types import NavAnalysisResult
from backend.common.utils import sum_origin_cash
from backend.models import PortfolioNavDaily
from backend.services.cache import CacheRepository
from backend.services.calculation.nav import (
    assemble_nav_analysis,
    benchmark_windows,
    clip_windows_to_range,
    compute_nav_rows,
    group_operations,
    holding_windows,
    holdings_at,
    resolve_start_date,
)
from backend.services.calculation.nav.benchmarks import BENCHMARKS
from backend.services.data_sync import (
    ensure_daily_prices_for_windows,
    ensure_hkd_cny_rates,
    load_daily_closes,
)


RECENT_SPAN_DAYS = {
    'week': 7,
    'month': 31,
    'quarter': 92,
}


def _needs_hk_fx(start_holdings: dict[str, float], price_windows: dict) -> bool:
    return any(is_hk_code(code) for code in start_holdings) or any(
        is_hk_code(code) for code in price_windows
    )


def _recent_span_name(span: str | None) -> str:
    chosen = span or 'month'
    if chosen not in RECENT_SPAN_DAYS:
        raise ValueError('span 须为 week、month 或 quarter')
    return chosen


class NavAnalysis:
    """净值分析：日净值刷新 + 展示序列/区间指标。"""

    @classmethod
    def build(cls, user: User) -> NavAnalysisResult:
        """从库内日净值 + 现金信息组装 API / 缓存 payload。"""
        rows = list(
            PortfolioNavDaily.objects.filter(user=user)
            .order_by('date')
            .values_list('date', 'nav')
        )
        income_cash, cash_flow_list = CacheRepository.get_user_cash_info(user)
        closes = (
            load_daily_closes(
                [spec.code for spec in BENCHMARKS],
                rows[0][0],
                rows[-1][0],
            )
            if rows
            else {}
        )
        return assemble_nav_analysis(
            list(rows),
            income_cash,
            sum_origin_cash(cash_flow_list),
            updated_at=datetime.now(timezone.utc).isoformat(),
            benchmark_closes=closes,
        )

    @classmethod
    def _sync_benchmarks(cls, user: User, end: date) -> None:
        """把三条指数收盘补到用户净值区间。失败只留空点，不中断净值刷新。"""
        first = (
            PortfolioNavDaily.objects.filter(user=user)
            .order_by('date')
            .values_list('date', flat=True)
            .first()
        )
        if first is None or not (windows := benchmark_windows(first, end)):
            return
        try:
            ensure_daily_prices_for_windows(windows)
        except Exception:
            logger.exception(f"[nav] 用户 {user.pk} 指数收盘补拉失败")

    @classmethod
    def _seed_row(
        cls,
        user: User,
        mode: str,
        end: date,
        span_name: str | None,
    ) -> PortfolioNavDaily | None:
        """增量取最后一条；区间刷新取窗口起点之前的最后一条。"""
        rows = PortfolioNavDaily.objects.filter(user=user)
        if mode == 'recent':
            window_start = end - timedelta(days=RECENT_SPAN_DAYS[span_name or 'month'])
            rows = rows.filter(date__lt=window_start)
        return rows.order_by('-date').first()

    @classmethod
    def refresh(
        cls,
        user: User,
        *,
        mode: str = 'incremental',
        span: str | None = None,
    ) -> int:
        """拉取交易/出入金并刷新日净值写库。返回写入行数。

        mode: incremental | recent | full。
        recent 用 span（week | month | quarter）决定回看自然日，只覆盖种子日之后的尾部。
        """
        if mode not in ('incremental', 'recent', 'full'):
            raise ValueError('mode 须为 incremental、recent 或 full')
        span_name = _recent_span_name(span) if mode == 'recent' else None

        operation_list = CacheRepository.get_user_operations(user)
        _income_cash, cash_flow_list = CacheRepository.get_user_cash_info(user)

        end = TradingCalendar.latest_closed_session()
        all_ops, _ops_by_date = group_operations(operation_list)

        start_nav = 1.0
        start_units = 0.0
        start_cash = 0.0
        start_holdings: dict[str, float] = {}
        range_start = None
        event_cutoff = None

        if mode in ('incremental', 'recent'):
            if (seed := cls._seed_row(user, mode, end, span_name)) is not None:
                nxt = TradingCalendar.next_session(seed.date)
                if nxt is None or nxt > end:
                    logger.info(f"[nav] 用户 {user.pk} 净值已是最新 {seed.date}")
                    cls._sync_benchmarks(user, end)
                    return 0
                range_start = nxt
                start_nav = seed.nav
                start_units = seed.units
                start_cash = seed.cash
                start_holdings = holdings_at(operation_list, seed.date)
                event_cutoff = seed.date
            else:
                mode = 'full'
                span_name = None

        if mode == 'full' or range_start is None:
            if (origin := resolve_start_date(all_ops, cash_flow_list)) is None:
                PortfolioNavDaily.objects.filter(user=user).delete()
                logger.info(f"[nav] 用户 {user.pk} 无交易/出入金，已清空净值")
                return 0
            range_start = origin
            event_cutoff = None
            start_nav = 1.0
            start_units = 0.0
            start_cash = 0.0
            start_holdings = {}

        if not (sessions := TradingCalendar.sessions_between(range_start, end)):
            logger.info(f"[nav] 用户 {user.pk} 无待计算交易日")
            cls._sync_benchmarks(user, end)
            return 0

        windows = holding_windows(operation_list, end)
        price_windows = clip_windows_to_range(
            windows,
            range_start,
            end,
            seed_date=event_cutoff,
        )
        prices = (
            ensure_daily_prices_for_windows(price_windows)
            if price_windows
            else {}
        )
        hkd_cny_rates = (
            ensure_hkd_cny_rates(event_cutoff or range_start, end)
            if _needs_hk_fx(start_holdings, price_windows)
            else {}
        )

        rows = compute_nav_rows(
            operation_list=operation_list,
            cash_flow_list=cash_flow_list,
            sessions=sessions,
            prices=prices,
            hkd_cny_rates=hkd_cny_rates,
            event_cutoff=event_cutoff,
            start_nav=start_nav,
            start_units=start_units,
            start_cash=start_cash,
            start_holdings=start_holdings,
        )

        objs = [
            PortfolioNavDaily(
                user=user,
                date=row.date,
                nav=row.nav,
                units=row.units,
                asset=row.asset,
                cash=row.cash,
            )
            for row in rows
        ]
        with transaction.atomic():
            if mode == 'full':
                PortfolioNavDaily.objects.filter(user=user).delete()
            PortfolioNavDaily.objects.bulk_create(
                objs,
                update_conflicts=True,
                unique_fields=['user', 'date'],
                update_fields=['nav', 'units', 'asset', 'cash'],
            )

        cls._sync_benchmarks(user, end)
        label = f"{mode}:{span_name}" if span_name else mode
        logger.info(
            f"[nav] 用户 {user.pk} {label} 刷新完成: {len(rows)} 天 "
            f"({sessions[0]} ~ {sessions[-1]}), 取价股票 {len(price_windows)}"
        )
        return len(rows)
