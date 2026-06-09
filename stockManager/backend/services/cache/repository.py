"""缓存仓库门面"""
from typing import Iterable

from django.contrib.auth.models import User

from ...common.cache import Cache
from ...common import logger
from ...common.types import (
    CalculatedResult,
    MarketsData,
    OperationDict,
    CashFlowList,
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
    def get_stock_meta_dict(cls) -> dict[str, StockMetaModel]:
        return meta_store.get_stock_meta_dict()

    @classmethod
    def query_stock_prices(cls, code_list: list[str]) -> RealtimePriceDict:
        return price_store.query_prices(code_list)

    @classmethod
    def get_hkd_cny_rate(cls, user_codes: Iterable[str]) -> float:
        return fx_store.get_hkd_cny_rate(user_codes)

    @classmethod
    def get_markets_metadata(cls) -> MarketsData:
        return price_store.get_markets_metadata()

    @classmethod
    def get_user_watchlist(cls, user: User) -> list[WatchItemDict]:
        return watch_store.get_user_watchlist(user)

    @classmethod
    def get_valuations(cls, codes: list[str], price_map: RealtimePriceDict) -> dict[str, ValuationData]:
        return valuation_store.get_valuations(codes, price_map)

    @classmethod
    def get_hist_highs(cls, codes: list[str]) -> dict[str, float | None]:
        return hist_high_store.get_hist_highs(codes)

    @classmethod
    def clear_all(cls) -> int:
        deleted_count = Cache.delete_pattern("*")
        logger.info(f"[Redis] 管理员清理全部缓存，删除 {deleted_count} 个 key")
        return deleted_count
