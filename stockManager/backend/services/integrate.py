"""用户数据集成（外观模式）：协调缓存、计算、分红等服务。"""
from typing import cast

from django.contrib.auth.models import User

from backend.common import logger
from backend.common.types import (
    CalculatedResult,
    DividendUpdateData,
    OperationData,
    OperationDataDict,
    WatchResultItem,
)
from backend.models import Info, WatchItem
from backend.services.cache import CacheRepository
from backend.services.calculation import Calculator
from backend.services.calculation.watchlist import build_watchlist
from backend.services.dividend import Dividend


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

        cached = CacheRepository.get_calculated_target(user, user_codes)
        if cached is not None:
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
        try:
            item = WatchItem.objects.get(user=user, stock_meta__code=code)
        except WatchItem.DoesNotExist as exc:
            raise WatchItem.DoesNotExist(f"关注项不存在: {code}") from exc
        item.hidden = hidden
        item.save(update_fields=["hidden"])
        logger.info(f"用户 {user.username} 设置关注隐藏: {code}={hidden}")

    @classmethod
    def get_watchlist(cls, user: User) -> list[WatchResultItem]:
        items = CacheRepository.get_user_watchlist(user)
        if not items:
            return []

        codes = [item["code"] for item in items]
        market_data = CacheRepository.load_watchlist_market_data(codes)
        return build_watchlist(
            items,
            market_data.prices,
            market_data.valuations,
            market_data.hist_highs,
        )
