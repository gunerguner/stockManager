"""缓存仓库门面：对外统一入口，聚合多 store 的编排调用"""
from dataclasses import dataclass
from typing import Iterable

from django.contrib.auth.models import User

from ...common.cache import Cache
from ...common import logger
from ...common.types import (
    CalculatedResult,
    CashFlowList,
    MarketsData,
    OperationDict,
    RealtimePriceDict,
    ValuationData,
    WatchItemDict,
)
from ...models import StockMeta as StockMetaModel
from . import fx_store
from . import hist_high_store
from . import meta_store
from . import price_store
from . import user_store
from . import valuation_store
from . import watch_store


@dataclass(frozen=True)
class CalculationInputs:
    income_cash: float
    cash_flow_list: CashFlowList
    hkd_cny_rate: float
    prices: RealtimePriceDict
    stock_meta: dict[str, StockMetaModel]
    markets: MarketsData


@dataclass(frozen=True)
class WatchlistMarketData:
    prices: RealtimePriceDict
    valuations: dict[str, ValuationData]
    hist_highs: dict[str, float | None]


class CacheRepository:
    @classmethod
    def get_user_operations(cls, user: User) -> OperationDict:
        return user_store.get_user_operations(user)

    @classmethod
    def get_calculated_target(
        cls,
        user: User,
        user_codes: Iterable[str] | None = None,
    ) -> CalculatedResult | None:
        return user_store.get_calculated_target(user, user_codes)

    @classmethod
    def set_calculated_target(
        cls,
        user_id: int,
        result: CalculatedResult,
        user_codes: Iterable[str],
    ) -> None:
        user_store.set_calculated_target(user_id, result, user_codes)

    @classmethod
    def get_stock_meta_dict(cls) -> dict[str, StockMetaModel]:
        return meta_store.get_stock_meta_dict()

    @classmethod
    def get_user_watchlist(cls, user: User) -> list[WatchItemDict]:
        return watch_store.get_user_watchlist(user)

    @classmethod
    def load_calculation_inputs(cls, user: User, operation_list: OperationDict) -> CalculationInputs:
        """聚合持仓计算所需的现金流、汇率、行情与元数据。"""
        user_codes = list(operation_list.keys())
        income_cash, cash_flow_list = user_store.get_user_cash_info(user)
        return CalculationInputs(
            income_cash=income_cash,
            cash_flow_list=cash_flow_list,
            hkd_cny_rate=fx_store.get_hkd_cny_rate(user_codes),
            prices=price_store.query_prices(user_codes),
            stock_meta=meta_store.get_stock_meta_dict(),
            markets=price_store.get_markets_metadata(),
        )

    @classmethod
    def load_watchlist_market_data(cls, codes: list[str]) -> WatchlistMarketData:
        """聚合关注列表所需的行情、估值与历史高价。"""
        prices = price_store.query_prices(codes)
        return WatchlistMarketData(
            prices=prices,
            valuations=valuation_store.get_valuations(codes, prices),
            hist_highs=hist_high_store.get_hist_highs(codes),
        )

    @classmethod
    def clear_all(cls) -> int:
        deleted_count = Cache.delete_pattern("*")
        logger.info(f"[Redis] 管理员清理全部缓存，删除 {deleted_count} 个 key")
        return deleted_count
