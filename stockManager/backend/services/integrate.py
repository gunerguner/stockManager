"""用户数据集成（外观模式）：协调缓存、计算、分红等服务。"""
from django.contrib.auth.models import User

from ..common import logger
from ..common.types import CalculatedResult, DividendUpdateData, OperationDataDict
from ..models import Info
from .cache import CacheRepository
from .calculation import Calculator
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
            cls._ensure_hkd_cny_rate(cached, user_codes)
            return cached

        income_cash, cash_flow_list = CacheRepository.get_user_cash_info(user)
        hkd_cny_rate = CacheRepository.get_hkd_cny_rate(user_codes)
        stock_list = Calculator.calculate_stock_list(operation_list)
        overall = Calculator.calculate_overall(
            stock_list, income_cash, cash_flow_list, hkd_cny_rate
        )

        result: CalculatedResult = {
            "stocks": stock_list,
            "overall": overall,
            "markets": CacheRepository.get_markets_metadata(),
        }
        CacheRepository.set_calculated_target(user.id, result, user_codes)
        return result

    @staticmethod
    def _ensure_hkd_cny_rate(result: CalculatedResult, user_codes: list[str]) -> None:
        """旧版 calculated_target 缓存可能缺少 hkdCnyRate，命中缓存时补全供前端展示。"""
        overall = result.setdefault("overall", {})
        if overall.get("hkdCnyRate") is None:
            overall["hkdCnyRate"] = CacheRepository.get_hkd_cny_rate(user_codes)

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
