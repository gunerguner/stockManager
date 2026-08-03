"""用户数据集成（外观模式）：协调缓存、计算、分红等服务。"""
from typing import cast

from django.contrib.auth.models import User

from backend.common import logger
from backend.common.types import (
    CalculatedResult,
    DividendUpdateData,
    NavAnalysisResult,
    OperationData,
    OperationDataDict,
    WatchResultItem,
)
from backend.models import Info
from backend.services.app.dividend import Dividend
from backend.services.app.nav import NavAnalysis
from backend.services.app.watchlist import Watchlist
from backend.services.cache import CacheRepository
from backend.services.calculation import Calculator


class Integrate:
    @classmethod
    def get_operations(cls, user: User) -> OperationDataDict:
        operation_list = CacheRepository.get_user_operations(user)
        return {
            code: [cast(OperationData, op.to_dict()) for op in reversed(ops)]
            for code, ops in operation_list.items()
        }

    @classmethod
    def get_calculated_result(cls, user: User) -> CalculatedResult:
        operation_list = CacheRepository.get_user_operations(user)
        user_codes = list(operation_list.keys())

        if (cached := CacheRepository.get_calculated_target(user, user_codes)) is not None:
            return cached

        inputs = CacheRepository.load_calculation_inputs(user, operation_list)
        stock_list = Calculator.calculate_stock_list(
            operation_list,
            inputs.prices,
            inputs.stock_meta,
            inputs.hkd_cny_rate,
        )
        overall = Calculator.calculate_overall(
            stock_list,
            inputs.income_cash,
            inputs.cash_flow_list,
            inputs.hkd_cny_rate,
        )

        result: CalculatedResult = {
            "stocks": stock_list,
            "overall": overall,
            "markets": inputs.markets,
        }
        CacheRepository.set_calculated_target(user.pk, result, user_codes)
        return result

    @classmethod
    def get_nav_analysis(cls, user: User) -> NavAnalysisResult:
        if (cached := CacheRepository.get_nav_analysis(user.pk)) is not None:
            return cached
        result = NavAnalysis.build(user)
        CacheRepository.set_nav_analysis(user.pk, result)
        return result

    @classmethod
    def refresh_nav(cls, user: User, mode: str = 'incremental') -> dict:
        written = NavAnalysis.refresh(user, mode=mode)
        result = NavAnalysis.build(user)
        CacheRepository.set_nav_analysis(user.pk, result)
        return {
            'written': written,
            'pointCount': len(result.get('points') or []),
        }

    @classmethod
    def generate_dividend(cls, user: User) -> list[DividendUpdateData]:
        operation_list = CacheRepository.get_user_operations(user)
        return Dividend.generate_dividend(user, operation_list)

    @classmethod
    def update_income_cash(cls, user: User, income_cash: float) -> None:
        Info.objects.update_or_create(
            user=user,
            info_type=Info.InfoType.INCOME_CASH,
            defaults={"value": str(income_cash)},
        )
        logger.info(f"用户 {user.username} 更新收益现金: {income_cash}")

    @classmethod
    def set_watch_hidden(cls, user: User, code: str, hidden: bool) -> None:
        Watchlist.set_hidden(user, code, hidden)

    @classmethod
    def get_watchlist(cls, user: User) -> list[WatchResultItem]:
        if not (items := CacheRepository.get_user_watchlist(user)):
            return []
        codes = [item["code"] for item in items]
        market_data = CacheRepository.load_watchlist_market_data(codes)
        return Watchlist.build(
            items,
            market_data.prices,
            market_data.valuations,
            market_data.hist_highs,
        )
