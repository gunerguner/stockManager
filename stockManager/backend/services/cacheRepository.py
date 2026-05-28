"""缓存仓库层"""
import json
from datetime import datetime

from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models.base import ModelState

from ..common.cache import Cache
from ..common import logger
from ..common.tradingCalendar import TradingCalendar, TZ_SHANGHAI
from ..models import Operation, Info, CashFlow, StockMeta as StockMetaModel
from ..common.utils import format_operations
from ..common.types import CalculatedResult, OperationDict, CashFlowList


class CacheRepository:
    """缓存仓库层"""
    
    KEY_USER_OPERATIONS = "user:{user_id}:operations"
    KEY_USER_CASH_INFO = "user:{user_id}:cash_info"
    KEY_CALCULATED_TARGET = "user:{user_id}:calculated_target"
    KEY_STOCK_META_ALL = "stock:meta:all"
    KEY_STOCK_PRICE = "stock:price:{code}"
    KEY_STOCK_PRICE_TIMESTAMP = "stock:price:timestamp"
    KEY_STOCK_NAME_SYNC_MARK = "stock:name:sync:mark"
    
    TTL_USER_DATA = 36000
    TTL_CALCULATED_TARGET = 86400
    TTL_STOCK_META = 86400
    TTL_STOCK_PRICE = 86400
    TTL_STOCK_NAME_SYNC = 86400
    
    @classmethod
    def _should_refresh_cache(cls) -> bool:
        """判断是否需要刷新缓存"""
        # 如果当前在交易时间,需要实时查询
        if TradingCalendar.is_current_time_in_trading_hours():
            return True
        
        # 检查缓存时间戳是否过期(是否经过了交易时间)
        cached_timestamp = cls.get_stock_price_timestamp()
        if not cached_timestamp:
            return True
        
        cached_time = datetime.fromisoformat(cached_timestamp)
        current_time = datetime.now(TZ_SHANGHAI)
        return TradingCalendar.is_trading_time_passed(cached_time, current_time)
    
    @classmethod
    def _serialize_operations(cls, operations: OperationDict) -> str:
        return json.dumps({
            code: [
                {
                    'id': op.id,
                    'date': str(op.date),
                    'sortOrder': op.sortOrder,
                    'operationType': op.operationType,
                    'price': op.price,
                    'count': op.count,
                    'fee': op.fee,
                    'comment': op.comment,
                    'cash': op.cash,
                    'stock': op.stock,
                    'reserve': op.reserve,
                }
                for op in op_list
            ]
            for code, op_list in operations.items()
        })
    
    @classmethod
    def _operation_from_cache(cls, code: str, op_data: dict, user_id: int) -> Operation:
        op = Operation.__new__(Operation)

        state = ModelState()
        state.adding = False
        state.db = 'default'

        op._state = state
        op.id = op_data['id']
        op.user_id = user_id
        op.code = code
        op.date = datetime.strptime(op_data['date'], '%Y-%m-%d').date()
        op.sortOrder = op_data.get('sortOrder', 0)
        op.operationType = op_data['operationType']
        op.price = op_data['price']
        op.count = op_data['count']
        op.fee = op_data['fee']
        op.comment = op_data['comment']
        op.cash = op_data['cash']
        op.stock = op_data['stock']
        op.reserve = op_data['reserve']
        return op

    @classmethod
    def _deserialize_operations(cls, data: str, user: User) -> OperationDict:
        operations_dict = json.loads(data)
        user_id = user.id
        return {
            code: [cls._operation_from_cache(code, op_data, user_id) for op_data in op_list]
            for code, op_list in operations_dict.items()
        }
    
    @classmethod
    def _get_user_operations_cache(cls, user: User) -> OperationDict | None:
        key = cls.KEY_USER_OPERATIONS.format(user_id=user.id)
        data = cache.get(key)
        return cls._deserialize_operations(data, user) if data else None
    
    @classmethod
    def _set_user_operations_cache(cls, user: User, operations: OperationDict) -> None:
        key = cls.KEY_USER_OPERATIONS.format(user_id=user.id)
        data = cls._serialize_operations(operations)
        cache.set(key, data, cls.TTL_USER_DATA)
    
    @classmethod
    def clear_user_operations(cls, user_id: int) -> None:
        cache.delete(cls.KEY_USER_OPERATIONS.format(user_id=user_id))
    
    @classmethod
    def _get_user_cash_info_cache(cls, user: User) -> tuple | None:
        key = cls.KEY_USER_CASH_INFO.format(user_id=user.id)
        data = cache.get(key)
        return (data['income_cash'], data['cash_flow_list']) if data else None
    
    @classmethod
    def _set_user_cash_info_cache(cls, user: User, income_cash: float, cash_flow_list: CashFlowList) -> None:
        cache.set(
            cls.KEY_USER_CASH_INFO.format(user_id=user.id),
            {'income_cash': income_cash, 'cash_flow_list': cash_flow_list},
            cls.TTL_USER_DATA
        )
    
    @classmethod
    def clear_user_cash_info(cls, user_id: int) -> None:
        cache.delete(cls.KEY_USER_CASH_INFO.format(user_id=user_id))
    

    @classmethod
    def get_calculated_target(cls, user: User) -> CalculatedResult | None:
        if cls._should_refresh_cache():
            return None
        return cache.get(cls.KEY_CALCULATED_TARGET.format(user_id=user.id))
    
    @classmethod
    def set_calculated_target(cls, user_id: int, result: CalculatedResult) -> None:
        if TradingCalendar.is_current_time_in_trading_hours():
            return
        cache.set(cls.KEY_CALCULATED_TARGET.format(user_id=user_id), result, cls.TTL_CALCULATED_TARGET)
    
    @classmethod
    def clear_calculated_target(cls, user_id: int) -> None:
        cache.delete(cls.KEY_CALCULATED_TARGET.format(user_id=user_id))
    
    @classmethod
    def clear_all_calculated_targets(cls) -> None:
        deleted_count = Cache.delete_pattern("user:*:calculated_target")
        if deleted_count > 0:
            logger.info(f"[Redis] 价格更新，清除 {deleted_count} 个用户的计算结果缓存")
    
    @classmethod
    def _get_stock_meta_all_cache(cls) -> dict | None:
        return cache.get(cls.KEY_STOCK_META_ALL)
    
    @classmethod
    def _set_stock_meta_all_cache(cls, meta_dict: dict) -> None:
        cache.set(
            cls.KEY_STOCK_META_ALL,
            {code: {'code': meta.code, 'name': meta.name, 'isNew': meta.isNew, 'stockType': meta.stockType}
             for code, meta in meta_dict.items()},
            cls.TTL_STOCK_META
        )
    
    @classmethod
    def clear_stock_meta_all(cls) -> None:
        cache.delete(cls.KEY_STOCK_META_ALL)

    @classmethod
    def has_stock_name_synced(cls) -> bool:
        return cache.get(cls.KEY_STOCK_NAME_SYNC_MARK) is not None

    @classmethod
    def mark_stock_name_synced(cls) -> None:
        cache.set(cls.KEY_STOCK_NAME_SYNC_MARK, True, cls.TTL_STOCK_NAME_SYNC)
    
    @classmethod
    def get_stock_price(cls, code: str) -> dict | None:
        return cache.get(cls.KEY_STOCK_PRICE.format(code=code))
    
    @classmethod
    def get_stock_prices_batch(cls, code_list: list[str]) -> dict[str, dict | None]:
        if not code_list:
            return {}
        try:
            keys = [cls.KEY_STOCK_PRICE.format(code=code) for code in code_list]
            result = Cache.get_many(keys)
            return {code: result.get(keys[i]) for i, code in enumerate(code_list)}
        except Exception as e:
            logger.error(f"批量获取股价缓存失败: {e}")
            return {code: cls.get_stock_price(code) for code in code_list}
    
    @classmethod
    def set_stock_price(cls, code: str, price_data: dict) -> None:
        cache.set(cls.KEY_STOCK_PRICE.format(code=code), price_data, cls.TTL_STOCK_PRICE)
    
    @classmethod
    def get_stock_price_timestamp(cls) -> str | None:
        return cache.get(cls.KEY_STOCK_PRICE_TIMESTAMP)
    
    @classmethod
    def set_stock_price_timestamp(cls, timestamp: str) -> None:
        cache.set(cls.KEY_STOCK_PRICE_TIMESTAMP, timestamp, cls.TTL_STOCK_PRICE)
        cls.clear_all_calculated_targets()

    @classmethod
    def get_stock_prices_with_cache(cls, code_list: list[str]) -> tuple[dict[str, dict], list[str]]:
        if not code_list:
            return {}, []
        
        if cls._should_refresh_cache():
            return {}, code_list.copy()
        
        batch_result = cls.get_stock_prices_batch(code_list)
        cached_result = {
            code: price_data
            for code in code_list
            if (price_data := batch_result.get(code))
        }
        missing_codes = [code for code in code_list if code not in cached_result]
        return cached_result, missing_codes
    
    @classmethod
    def set_stock_prices_batch(cls, prices: dict[str, dict], timestamp: str | None = None) -> None:
        if not prices:
            return

        Cache.set_many(
            {cls.KEY_STOCK_PRICE.format(code=code): price_data for code, price_data in prices.items()},
            cls.TTL_STOCK_PRICE,
        )

        # 设置时间戳
        cls.set_stock_price_timestamp(
            timestamp or datetime.now(TZ_SHANGHAI).isoformat()
        )
    
    @classmethod
    def get_user_operations(cls, user: User) -> OperationDict:
        cached = cls._get_user_operations_cache(user)
        if cached is not None:
            return cached
        operations = format_operations(Operation.objects.filter(user=user).order_by('date', 'sortOrder', 'id'))
        cls._set_user_operations_cache(user, operations)
        return operations
    
    @classmethod
    def get_user_cash_info(cls, user: User) -> tuple[float, CashFlowList]:
        cached = cls._get_user_cash_info_cache(user)
        if cached is not None:
            return cached
        income_info = Info.objects.filter(user=user, info_type=Info.InfoType.INCOME_CASH).first()
        income_cash = float(income_info.value) if income_info else 0.0
        cash_flow_list = [
            {'date': str(flow.transaction_date), 'amount': float(flow.amount)}
            for flow in CashFlow.objects.filter(user=user).order_by('-transaction_date')
        ]
        cls._set_user_cash_info_cache(user, income_cash, cash_flow_list)
        return income_cash, cash_flow_list
    
    @classmethod
    def get_stock_meta_dict(cls) -> dict[str, StockMetaModel]:
        cached_data = cls._get_stock_meta_all_cache()
        if cached_data:
            return {
                code: StockMetaModel(
                    code=data['code'],
                    name=data.get('name', ''),
                    isNew=data['isNew'],
                    stockType=data['stockType']
                )
                for code, data in cached_data.items()
            }
        meta_dict = {meta.code: meta for meta in StockMetaModel.objects.all()}
        cls._set_stock_meta_all_cache(meta_dict)
        return meta_dict
    
    @classmethod
    def clear_user_cache(cls, user_id: int) -> None:
        cls.clear_user_operations(user_id)
        cls.clear_user_cash_info(user_id)
        cls.clear_calculated_target(user_id)

    @classmethod
    def clear_all(cls) -> int:
        deleted_count = Cache.delete_pattern("*")
        logger.info(f"[Redis] 管理员清理全部缓存，删除 {deleted_count} 个 key")
        return deleted_count
