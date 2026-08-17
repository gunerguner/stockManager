"""缓存仓库门面：对外统一入口，聚合多 store 的编排调用"""
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Iterable

from django.contrib.auth.models import User

from backend.common import logger
from backend.common.cache import Cache
from backend.common.types import (
    CalculatedResult,
    CashFlowList,
    MarketsData,
    NavAnalysisResult,
    OperationDict,
    RealtimePriceDict,
    ValuationData,
    WatchItemDict,
)
from backend.models import StockMeta as StockMetaModel
from backend.services.cache.market import fx
from backend.services.cache.market import hist_high
from backend.services.cache.market import meta
from backend.services.cache.market import prices
from backend.services.cache.market import valuation
from backend.services.cache.user import store as user_store
from backend.services.cache.user import watchlist


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
    def get_user_cash_info(cls, user: User) -> tuple[float, CashFlowList]:
        return user_store.get_user_cash_info(user)

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
    def get_nav_analysis(cls, user_id: int) -> NavAnalysisResult | None:
        return user_store.get_nav_analysis(user_id)

    @classmethod
    def set_nav_analysis(cls, user_id: int, result: NavAnalysisResult) -> None:
        user_store.set_nav_analysis(user_id, result)

    @classmethod
    def get_hkd_cny_rate(cls, user_codes: Iterable[str]) -> float:
        return fx.get_hkd_cny_rate(user_codes)

    @classmethod
    def get_stock_meta_dict(cls) -> dict[str, StockMetaModel]:
        return meta.get_stock_meta_dict()

    @classmethod
    def get_user_watchlist(cls, user: User) -> list[WatchItemDict]:
        return watchlist.get_user_watchlist(user)

    @classmethod
    def load_calculation_inputs(cls, user: User, operation_list: OperationDict) -> CalculationInputs:
        """聚合持仓计算所需的现金流、汇率、行情与元数据。"""
        user_codes = list(operation_list.keys())
        income_cash, cash_flow_list = cls.get_user_cash_info(user)
        return CalculationInputs(
            income_cash=income_cash,
            cash_flow_list=cash_flow_list,
            hkd_cny_rate=cls.get_hkd_cny_rate(user_codes),
            prices=prices.query_prices(user_codes),
            stock_meta=meta.get_stock_meta_dict(),
            markets=prices.get_markets_metadata(),
        )

    @classmethod
    def load_watchlist_market_data(cls, codes: list[str]) -> WatchlistMarketData:
        """聚合关注列表所需的行情、估值与历史高价。"""
        prices_map = prices.query_prices(codes)

        cached_vals, missing_vals = valuation.get_cached_valuations(codes)
        cached_hist, missing_hist = hist_high.get_cached_hist_highs(codes)

        valuations = dict(cached_vals)
        hist_highs = dict(cached_hist)

        futures: list[tuple[str, Future]] = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            if missing_vals:
                futures.append((
                    "val",
                    executor.submit(valuation.fetch_and_cache_valuations, missing_vals, prices_map),
                ))
            if missing_hist:
                futures.append((
                    "hist",
                    executor.submit(hist_high.fetch_and_cache_hist_highs, missing_hist),
                ))

            for name, future in futures:
                if name == "val":
                    valuations.update(future.result())
                elif name == "hist":
                    hist_highs.update(future.result())

        return WatchlistMarketData(
            prices=prices_map,
            valuations=valuations,
            hist_highs=hist_highs,
        )

    @classmethod
    def clear_all(cls) -> int:
        deleted_count = Cache.delete_pattern("*")
        logger.info(f"[Redis] 管理员清理全部缓存，删除 {deleted_count} 个 key")
        return deleted_count
