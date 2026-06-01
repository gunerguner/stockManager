"""缓存仓库门面，对外保持 CacheRepository API 不变"""
from typing import Iterable

from django.contrib.auth.models import User

from ...common.cache import Cache
from ...common.market import Market
from ...common import logger
from ...common.types import CalculatedResult, OperationDict, CashFlowList
from ...models import StockMeta as StockMetaModel
from . import keys
from . import user_store
from . import price_store
from . import meta_store


class CacheRepository:
    """缓存仓库层"""

    KEY_USER_OPERATIONS = keys.KEY_USER_OPERATIONS
    KEY_USER_CASH_INFO = keys.KEY_USER_CASH_INFO
    KEY_CALCULATED_TARGET = keys.KEY_CALCULATED_TARGET
    KEY_STOCK_META_ALL = keys.KEY_STOCK_META_ALL
    KEY_STOCK_PRICE = keys.KEY_STOCK_PRICE
    KEY_STOCK_PRICE_TIMESTAMP = keys.KEY_STOCK_PRICE_TIMESTAMP
    KEY_STOCK_PRICE_TIMESTAMP_LEGACY = keys.KEY_STOCK_PRICE_TIMESTAMP_LEGACY
    KEY_FX_HKD_CNY = keys.KEY_FX_HKD_CNY
    KEY_STOCK_NAME_SYNC_MARK = keys.KEY_STOCK_NAME_SYNC_MARK

    TTL_USER_DATA = keys.TTL_USER_DATA
    TTL_CALCULATED_TARGET = keys.TTL_CALCULATED_TARGET
    TTL_STOCK_META = keys.TTL_STOCK_META
    TTL_STOCK_PRICE = keys.TTL_STOCK_PRICE
    TTL_STOCK_NAME_SYNC = keys.TTL_STOCK_NAME_SYNC
    TTL_FX = keys.TTL_FX

    @classmethod
    def _should_refresh_cache(cls) -> bool:
        return price_store.should_refresh_cache()

    @classmethod
    def clear_user_operations(cls, user_id: int) -> None:
        user_store.clear_user_operations(user_id)

    @classmethod
    def clear_user_cash_info(cls, user_id: int) -> None:
        user_store.clear_user_cash_info(user_id)

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
    def clear_calculated_target(cls, user_id: int) -> None:
        user_store.clear_calculated_target(user_id)

    @classmethod
    def clear_all_calculated_targets(cls) -> None:
        user_store.clear_all_calculated_targets()

    @classmethod
    def clear_stock_meta_all(cls) -> None:
        meta_store.clear_stock_meta_all()

    @classmethod
    def has_stock_name_synced(cls) -> bool:
        return meta_store.has_stock_name_synced()

    @classmethod
    def mark_stock_name_synced(cls) -> None:
        meta_store.mark_stock_name_synced()

    @classmethod
    def get_stock_price(cls, code: str) -> dict | None:
        return price_store.get_stock_price(code)

    @classmethod
    def get_stock_prices_batch(cls, code_list: list[str]) -> dict[str, dict | None]:
        return price_store.get_stock_prices_batch(code_list)

    @classmethod
    def set_stock_price(cls, code: str, price_data: dict) -> None:
        price_store.set_stock_price(code, price_data)

    @classmethod
    def get_stock_price_timestamp(cls, market: Market = Market.CN) -> str | None:
        return price_store.get_stock_price_timestamp(market)

    @classmethod
    def set_stock_price_timestamp(cls, market: Market, timestamp: str) -> None:
        price_store.set_stock_price_timestamp(market, timestamp)

    @classmethod
    def get_stock_prices_with_cache(cls, code_list: list[str]) -> tuple[dict[str, dict], list[str]]:
        return price_store.get_stock_prices_with_cache(code_list)

    @classmethod
    def set_stock_prices_batch(cls, prices: dict[str, dict], timestamp: str | None = None) -> None:
        price_store.set_stock_prices_batch(prices, timestamp)

    @classmethod
    def get_user_operations(cls, user: User) -> OperationDict:
        return user_store.get_user_operations(user)

    @classmethod
    def get_user_cash_info(cls, user: User) -> tuple[float, CashFlowList]:
        return user_store.get_user_cash_info(user)

    @classmethod
    def get_stock_meta_dict(cls) -> dict[str, StockMetaModel]:
        return meta_store.get_stock_meta_dict()

    @classmethod
    def clear_user_cache(cls, user_id: int) -> None:
        user_store.clear_user_cache(user_id)

    @classmethod
    def clear_all(cls) -> int:
        deleted_count = Cache.delete_pattern("*")
        logger.info(f"[Redis] 管理员清理全部缓存，删除 {deleted_count} 个 key")
        return deleted_count
