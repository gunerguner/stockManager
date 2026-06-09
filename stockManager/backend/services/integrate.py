"""用户数据集成（外观模式）：协调缓存、计算、分红等服务。"""
from django.contrib.auth.models import User

from ..common import logger
from ..common.types import CalculatedResult, DividendUpdateData, OperationDataDict, WatchResultItem
from ..models import Info
from .cache import CacheRepository
from .calculation import Calculator, StockHold
from .dividend import Dividend


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
        market_data = CacheRepository.load_watchlist_market_data(codes)

        def _ratio(price: float | None, per_share: float | None) -> float | None:
            if price and per_share:
                return round(price / per_share, 2)
            return None

        result: list[WatchResultItem] = []
        for item in items:
            code = item["code"]
            price_data = market_data.prices.get(code, {})
            valuation = market_data.valuations.get(code, {})
            price_now = price_data.get("currentPrice")
            result.append(
                WatchResultItem(
                    code=code,
                    name=price_data.get("name", code),
                    holding=code in holding_set,
                    priceNow=price_now,
                    histHigh=market_data.hist_highs.get(code),
                    pe=_ratio(price_now, valuation.get("epsTtm")),
                    pb=_ratio(price_now, valuation.get("bvps")),
                    risk=item["risk"] or "",
                    opportunity=item["opportunity"] or "",
                    leftPoint=item["leftPoint"],
                    trendPoint=item["trendPoint"],
                    bloodPoint=item["bloodPoint"],
                )
            )
        return result
