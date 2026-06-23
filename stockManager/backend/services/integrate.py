"""用户数据集成（外观模式）：协调缓存、计算、分红等服务。"""
from django.contrib.auth.models import User

from backend.common import logger
from backend.common.types import CalculatedResult, DividendUpdateData, OperationDataDict, WatchResultItem
from backend.models import Info
from backend.services.cache import CacheRepository
from backend.services.calculation import Calculator, StockHold
from backend.services.calculation.watchlist import build_watchlist
from backend.services.dividend import Dividend


class Integrate:
    @classmethod
    def get_operations(cls, user: User) -> OperationDataDict:
        operation_list = CacheRepository.get_user_operations(user)
        return {
            code: [op.to_dict() for op in reversed(ops)]
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
        CacheRepository.set_calculated_target(user.id, result, user_codes)
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
    def get_watchlist(cls, user: User) -> list[WatchResultItem]:
        items = CacheRepository.get_user_watchlist(user)
        if not items:
            return []

        codes = [item["code"] for item in items]
        operation_list = CacheRepository.get_user_operations(user)
        holding_set = set(StockHold.get_holding_stocks(operation_list))

        # 尝试从持股页缓存中提取已持有股票的累计盈亏，用于  HoldingStatus 图标颜色
        holding_offset: dict[str, float] = {}
        user_codes = list(operation_list.keys())
        cached = CacheRepository.get_calculated_target(user, user_codes)
        if cached is not None:
            for stock in cached.get("stocks", []):
                if stock["code"] in holding_set:
                    holding_offset[stock["code"]] = stock["offsetTotal"]

        market_data = CacheRepository.load_watchlist_market_data(codes)

        return build_watchlist(
            items,
            market_data.prices,
            market_data.valuations,
            market_data.hist_highs,
            holding_set,
            holding_offset,
        )
