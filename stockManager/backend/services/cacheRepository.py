"""
缓存仓库层
封装所有业务相关的缓存逻辑，包括 Key、TTL、序列化、业务方法等
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models.base import ModelState

from ..common.cache import Cache
from ..common import logger
from ..models import Operation, Info, CashFlow, StockMeta as StockMetaModel
from ..common.utils import format_operations


class CacheRepository:
    """
    缓存仓库层
    
    封装所有业务相关的缓存逻辑，包括：
    - 业务 Key 定义
    - 业务 TTL 配置
    - 业务序列化/反序列化
    - 业务缓存方法
    - 业务数据获取方法（带数据库加载）
    """
    
    # ========== 业务配置 ==========
    
    # 缓存 Key 前缀
    KEY_USER_OPERATIONS = "user:{user_id}:operations"
    KEY_USER_CASH_INFO = "user:{user_id}:cash_info"
    KEY_CALCULATED_TARGET = "user:{user_id}:calculated_target"
    KEY_STOCK_META_ALL = "stock:meta:all"
    KEY_STOCK_PRICE = "stock:price:{code}"
    KEY_STOCK_PRICE_TIMESTAMP = "stock:price:timestamp"
    
    # 缓存过期时间（秒）
    TTL_USER_DATA = 36000  # 用户数据：10小时
    TTL_CALCULATED_TARGET = 86400  # 计算结果：24小时（通过价格变化主动刷新）
    TTL_STOCK_META = 86400  # 股票元数据：24小时
    TTL_STOCK_PRICE = 86400  # 股票价格：24小时（通过时间戳判断有效性）
    
    # ========== 序列化/反序列化 ==========
    
    @classmethod
    def _serialize_operations(cls, operations: Dict[str, List[Operation]]) -> str:
        """序列化操作记录"""
        data = {}
        for code, op_list in operations.items():
            data[code] = [
                {
                    'id': op.id,
                    'date': str(op.date),
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
        return json.dumps(data)
    
    @classmethod
    def _deserialize_operations(cls, data: str, user: User) -> Dict[str, List[Operation]]:
        """反序列化操作记录（优化版：减少对象创建开销）"""
        operations_dict = json.loads(data)
        result = {}
        
        user_id = user.id
        
        for code, op_list in operations_dict.items():
            operations = []
            for op_data in op_list:
                # 使用 __new__ 绕过 __init__
                op = Operation.__new__(Operation)
                
                # Django 模型必须的 _state 属性
                state = ModelState()
                state.adding = False
                state.db = 'default'
                op._state = state
                
                # 直接设置字段值
                op.id = op_data['id']
                op.user_id = user_id
                op.code = code
                op.date = datetime.strptime(op_data['date'], '%Y-%m-%d').date()
                op.operationType = op_data['operationType']
                op.price = op_data['price']
                op.count = op_data['count']
                op.fee = op_data['fee']
                op.comment = op_data['comment']
                op.cash = op_data['cash']
                op.stock = op_data['stock']
                op.reserve = op_data['reserve']
                
                operations.append(op)
            result[code] = operations
        
        return result
    
    # ========== 用户数据缓存方法 ==========
    
    # --- 用户操作记录缓存 ---
    
    @classmethod
    def _get_user_operations_cache(cls, user: User) -> Optional[Dict[str, List[Operation]]]:
        """获取用户操作记录缓存（仅缓存，不带数据库加载）"""
        key = cls.KEY_USER_OPERATIONS.format(user_id=user.id)
        data = cache.get(key)
        
        if data:
            return cls._deserialize_operations(data, user)
        
        return None
    
    @classmethod
    def _set_user_operations_cache(cls, user: User, operations: Dict[str, List[Operation]]) -> None:
        """设置用户操作记录缓存"""
        key = cls.KEY_USER_OPERATIONS.format(user_id=user.id)
        data = cls._serialize_operations(operations)
        cache.set(key, data, cls.TTL_USER_DATA)
    
    @classmethod
    def clear_user_operations(cls, user_id: int) -> None:
        """清除用户操作记录缓存"""
        key = cls.KEY_USER_OPERATIONS.format(user_id=user_id)
        cache.delete(key)
    
    # --- 用户资金信息缓存 ---
    
    @classmethod
    def _get_user_cash_info_cache(cls, user: User) -> Optional[tuple]:
        """获取用户资金信息缓存（仅缓存，不带数据库加载）"""
        key = cls.KEY_USER_CASH_INFO.format(user_id=user.id)
        data = cache.get(key)
        
        if data:
            return (data['income_cash'], data['cash_flow_list'])
        
        return None
    
    @classmethod
    def _set_user_cash_info_cache(cls, user: User, income_cash: float, cash_flow_list: List[Dict]) -> None:
        """设置用户资金信息缓存"""
        key = cls.KEY_USER_CASH_INFO.format(user_id=user.id)
        data = {
            'income_cash': income_cash,
            'cash_flow_list': cash_flow_list
        }
        cache.set(key, data, cls.TTL_USER_DATA)
    
    @classmethod
    def clear_user_cash_info(cls, user_id: int) -> None:
        """清除用户资金信息缓存"""
        key = cls.KEY_USER_CASH_INFO.format(user_id=user_id)
        cache.delete(key)
    
    # --- 计算结果缓存 ---
    
    @classmethod
    def get_calculated_target(cls, user: User) -> Optional[Dict[str, Any]]:
        """
        获取用户计算结果缓存（仅缓存，不从数据库加载）
        
        计算结果由业务逻辑计算后写入，这里只负责读取。
        """
        key = cls.KEY_CALCULATED_TARGET.format(user_id=user.id)
        return cache.get(key)
    
    @classmethod
    def set_calculated_target(cls, user_id: int, result: Dict[str, Any]) -> None:
        """
        设置用户计算结果缓存
        
        TTL 为 24 小时，实际缓存有效性由价格变化时主动清除决定。
        """
        key = cls.KEY_CALCULATED_TARGET.format(user_id=user_id)
        cache.set(key, result, cls.TTL_CALCULATED_TARGET)
    
    @classmethod
    def clear_calculated_target(cls, user_id: int) -> None:
        """清除单个用户的计算结果缓存"""
        key = cls.KEY_CALCULATED_TARGET.format(user_id=user_id)
        cache.delete(key)
    
    @classmethod
    def clear_all_calculated_targets(cls) -> None:
        """清除所有用户的计算结果缓存（在价格更新时调用）"""
        pattern = "stockmanager:1:user:*:calculated_target"
        deleted_count = Cache.delete_pattern(pattern)
        if deleted_count > 0:
            logger.info(f"[Redis] 价格更新，清除 {deleted_count} 个用户的计算结果缓存")
    
    # ========== 股票数据缓存方法 ==========
    
    # --- 股票元数据缓存 ---
    
    @classmethod
    def _get_stock_meta_all_cache(cls) -> Optional[Dict]:
        """获取所有股票元数据缓存（仅缓存，不带数据库加载）"""
        key = cls.KEY_STOCK_META_ALL
        return cache.get(key)
    
    @classmethod
    def _set_stock_meta_all_cache(cls, meta_dict: Dict) -> None:
        """设置所有股票元数据缓存"""
        key = cls.KEY_STOCK_META_ALL
        serialized_data = {
            code: {
                'code': meta.code,
                'isNew': meta.isNew,
                'stockType': meta.stockType,
            }
            for code, meta in meta_dict.items()
        }
        cache.set(key, serialized_data, cls.TTL_STOCK_META)
    
    @classmethod
    def clear_stock_meta_all(cls) -> None:
        """清除股票元数据缓存"""
        key = cls.KEY_STOCK_META_ALL
        cache.delete(key)
    
    # --- 股票实时价格缓存 ---
    
    @classmethod
    def get_stock_price(cls, code: str) -> Optional[Dict]:
        """获取单个股票实时价格缓存"""
        key = cls.KEY_STOCK_PRICE.format(code=code)
        data = cache.get(key)
        
        if data:
            return data
        
        return None
    
    @classmethod
    def get_stock_prices_batch(cls, code_list: List[str]) -> Dict[str, Optional[Dict]]:
        """批量获取股票实时价格缓存（使用 Pipeline 优化）"""
        if not code_list:
            return {}
        
        try:
            # 构建完整的 Redis key（包含前缀和版本）
            keys = [f"stockmanager:1:stock:price:{code}" for code in code_list]
            
            # 使用 Cache.get_many 批量获取
            result = Cache.get_many(keys)
            
            # 转换 key 格式（从完整 key 转回 code）
            return {code: result.get(keys[i]) for i, code in enumerate(code_list)}
        except Exception as e:
            logger.error(f"批量获取股价缓存失败: {e}")
            # 降级为单个获取
            return {code: cls.get_stock_price(code) for code in code_list}
    
    @classmethod
    def set_stock_price(cls, code: str, price_data: Dict) -> None:
        """
        设置股票实时价格缓存
        
        TTL 为 24 小时，实际缓存有效性由 RealtimePrice 的时间戳判断逻辑决定。
        """
        key = cls.KEY_STOCK_PRICE.format(code=code)
        cache.set(key, price_data, cls.TTL_STOCK_PRICE)
    
    @classmethod
    def get_stock_price_timestamp(cls) -> Optional[str]:
        """获取股票价格缓存时间戳"""
        key = cls.KEY_STOCK_PRICE_TIMESTAMP
        return cache.get(key)
    
    @classmethod
    def set_stock_price_timestamp(cls, timestamp: str) -> None:
        """
        设置股票价格缓存时间戳
        
        同时清除所有用户的计算结果缓存，因为价格已更新。
        """
        key = cls.KEY_STOCK_PRICE_TIMESTAMP
        cache.set(key, timestamp, cls.TTL_STOCK_PRICE)
        # 价格更新，清除所有用户的计算结果缓存
        cls.clear_all_calculated_targets()
    
    @classmethod
    def clear_all_stock_prices(cls) -> None:
        """清除所有股票价格缓存"""
        pattern = "stockmanager:stock:price:*"
        Cache.delete_pattern(pattern)
    
    # ========== 业务数据获取方法（带数据库加载） ==========
    
    @classmethod
    def get_user_operations(cls, user: User) -> Dict[str, List[Operation]]:
        """
        获取用户操作记录（自动处理缓存）
        
        如果缓存命中，直接返回；否则从数据库查询并写入缓存。
        """
        # 尝试从缓存获取
        cached = cls._get_user_operations_cache(user)
        if cached is not None:
            return cached
        
        # 缓存未命中，从数据库加载
        operations = format_operations(
            Operation.objects.filter(user=user).order_by("date")
        )
        
        # 写入缓存
        cls._set_user_operations_cache(user, operations)
        
        return operations
    
    @classmethod
    def get_user_cash_info(cls, user: User) -> tuple[float, List[Dict[str, Any]]]:
        """
        获取用户资金信息（自动处理缓存）
        
        返回 (income_cash, cash_flow_list)
        """
        # 尝试从缓存获取
        cached = cls._get_user_cash_info_cache(user)
        if cached is not None:
            return cached
        
        # 缓存未命中，从数据库查询
        income_info = Info.objects.filter(
            user=user, 
            info_type=Info.InfoType.INCOME_CASH
        ).first()
        income_cash = float(income_info.value) if income_info else 0.0
        
        cash_flows = CashFlow.objects.filter(user=user).order_by('-transaction_date')
        cash_flow_list = [
            {'date': str(flow.transaction_date), 'amount': float(flow.amount)}
            for flow in cash_flows
        ]
        
        # 写入缓存
        cls._set_user_cash_info_cache(user, income_cash, cash_flow_list)
        
        return income_cash, cash_flow_list
    
    @classmethod
    def get_stock_meta_dict(cls) -> Dict[str, StockMetaModel]:
        """
        获取股票元数据字典（自动处理缓存）
        
        如果缓存命中，反序列化后返回；否则从数据库查询并写入缓存。
        """
        # 尝试从缓存获取
        cached_data = cls._get_stock_meta_all_cache()
        if cached_data:
            # 反序列化
            result = {}
            for code, data in cached_data.items():
                meta = StockMetaModel(
                    code=data['code'],
                    isNew=data['isNew'],
                    stockType=data['stockType']
                )
                result[code] = meta
            return result
        
        # 缓存未命中，从数据库查询
        meta_dict = {
            meta.code: meta 
            for meta in StockMetaModel.objects.all()
        }
        
        # 写入缓存
        cls._set_stock_meta_all_cache(meta_dict)
        
        return meta_dict
    
    @classmethod
    def get_stock_meta(cls, code: str) -> Optional[StockMetaModel]:
        """获取单个股票元数据"""
        return cls.get_stock_meta_dict().get(code)
    
    # ========== 缓存清理 ==========
    
    @classmethod
    def clear_user_cache(cls, user_id: int) -> None:
        """清除用户所有缓存"""
        cls.clear_user_operations(user_id)
        cls.clear_user_cash_info(user_id)
        cls.clear_calculated_target(user_id)
