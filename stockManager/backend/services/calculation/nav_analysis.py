"""组合净值门面：刷新回放与展示指标组装（供 Integrate 调用）"""
from __future__ import annotations

from datetime import datetime, timezone

from django.contrib.auth.models import User

from backend.common.types import NavAnalysisResult
from backend.models import PortfolioNavDaily
from backend.services.cache import CacheRepository, user_store
from backend.services.calculation.nav import refresh_nav_for_user
from backend.services.calculation.nav_metrics import assemble_nav_analysis


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
        income_cash, cash_flow_list = user_store.get_user_cash_info(user)
        origin_cash = sum(float(f.get('amount') or 0) for f in cash_flow_list)
        return assemble_nav_analysis(
            list(rows),
            income_cash,
            origin_cash,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def refresh(cls, user: User, *, mode: str = 'incremental') -> int:
        """拉取交易/出入金并刷新日净值写库。返回写入行数。mode: incremental | full。"""
        if mode not in ('incremental', 'full'):
            raise ValueError(f"无效刷新模式: {mode}")
        operation_list = CacheRepository.get_user_operations(user)
        _income_cash, cash_flow_list = user_store.get_user_cash_info(user)
        return refresh_nav_for_user(
            user,
            operation_list,
            cash_flow_list,
            mode=mode,
        )
