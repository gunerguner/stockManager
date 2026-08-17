"""组合净值用例：刷新回放写库与展示指标组装"""
from datetime import datetime, timezone

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
    clip_windows_to_range,
    compute_nav_rows,
    group_operations,
    holding_windows,
    holdings_at,
    resolve_start_date,
)
from backend.services.data_sync import ensure_daily_prices_for_windows, ensure_hkd_cny_rates


def _needs_hk_fx(start_holdings: dict[str, float], price_windows: dict) -> bool:
    return any(is_hk_code(code) for code in start_holdings) or any(
        is_hk_code(code) for code in price_windows
    )


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
        return assemble_nav_analysis(
            list(rows),
            income_cash,
            sum_origin_cash(cash_flow_list),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def refresh(cls, user: User, *, mode: str = 'incremental') -> int:
        """拉取交易/出入金并刷新日净值写库。返回写入行数。mode: incremental | full。"""
        if mode not in ('incremental', 'full'):
            raise ValueError('mode 须为 incremental 或 full')

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

        if mode == 'incremental':
            if (
                last := PortfolioNavDaily.objects.filter(user=user)
                .order_by('-date')
                .first()
            ) is not None:
                nxt = TradingCalendar.next_session(last.date)
                if nxt is None or nxt > end:
                    logger.info(f"[nav] 用户 {user.pk} 净值已是最新 {last.date}")
                    return 0
                range_start = nxt
                start_nav = last.nav
                start_units = last.units
                start_cash = last.cash
                start_holdings = holdings_at(operation_list, last.date)
                event_cutoff = last.date
            else:
                mode = 'full'

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

        logger.info(
            f"[nav] 用户 {user.pk} {mode} 刷新完成: {len(rows)} 天 "
            f"({sessions[0]} ~ {sessions[-1]}), 取价股票 {len(price_windows)}"
        )
        return len(rows)
