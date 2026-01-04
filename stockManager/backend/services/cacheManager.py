"""
Redis 缓存管理工具类
提供统一的缓存操作接口，包括序列化、反序列化、过期时间管理
"""
import json
from datetime import datetime
from typing import Optional, Dict, List

from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models.base import ModelState
from django_redis import get_redis_connection

from ..common import logger
from ..models import Operation


class CacheManager:
    """Redis 缓存管理器"""
    
    # 缓存 Key 前缀
    KEY_USER_OPERATIONS = "user:{user_id}:operations"
    KEY_USER_CASH_INFO = "user:{user_id}:cash_info"
    KEY_CALCULATED_TARGET = "user:{user_id}:calculated_target"  # 计算结果缓存
    KEY_STOCK_META_ALL = "stock:meta:all"
    KEY_STOCK_PRICE = "stock:price:{code}"
    KEY_STOCK_PRICE_TIMESTAMP = "stock:price:timestamp"
    
    # 缓存过期时间（秒）
    TTL_USER_DATA = 36000  # 用户数据
    TTL_CALCULATED_TARGET_TRADING = 60  # 计算结果（交易时间）
    TTL_CALCULATED_TARGET_NON_TRADING = 36000  # 计算结果（非交易时间）
    TTL_STOCK_META = 86400  # 股票元数据
    TTL_STOCK_PRICE_TRADING = 60  # 股票价格（交易时间）
    TTL_STOCK_PRICE_NON_TRADING = 36000  # 股票价格（非交易时间）
    
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
    
    # ========== 用户操作记录缓存 ==========
    
    @classmethod
    def get_user_operations(cls, user: User) -> Optional[Dict[str, List[Operation]]]:
        """获取用户操作记录缓存"""
        key = cls.KEY_USER_OPERATIONS.format(user_id=user.id)
        data = cache.get(key)
        
        if data:
            return cls._deserialize_operations(data, user)
        
        return None
    
    @classmethod
    def set_user_operations(cls, user: User, operations: Dict[str, List[Operation]]) -> None:
        """设置用户操作记录缓存"""
        key = cls.KEY_USER_OPERATIONS.format(user_id=user.id)
        data = cls._serialize_operations(operations)
        cache.set(key, data, cls.TTL_USER_DATA)
    
    @classmethod
    def clear_user_operations(cls, user_id: int) -> None:
        """清除用户操作记录缓存"""
        key = cls.KEY_USER_OPERATIONS.format(user_id=user_id)
        cache.delete(key)
        
    
    # ========== 用户资金信息缓存 ==========
    
    @classmethod
    def get_user_cash_info(cls, user: User) -> Optional[tuple]:
        """获取用户资金信息缓存"""
        key = cls.KEY_USER_CASH_INFO.format(user_id=user.id)
        data = cache.get(key)
        
        if data:
            return (data['income_cash'], data['cash_flow_list'])
        
        return None
    
    @classmethod
    def set_user_cash_info(cls, user: User, income_cash: float, cash_flow_list: List[Dict]) -> None:
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
    
    # ========== 计算结果缓存 ==========
    
    @classmethod
    def get_calculated_target(cls, user_id: int) -> Optional[Dict]:
        """获取计算结果缓存"""
        key = cls.KEY_CALCULATED_TARGET.format(user_id=user_id)
        return cache.get(key)
    
    @classmethod
    def set_calculated_target(cls, user_id: int, result: Dict, ttl: int) -> None:
        """设置计算结果缓存"""
        key = cls.KEY_CALCULATED_TARGET.format(user_id=user_id)
        cache.set(key, result, ttl)
    
    @classmethod
    def clear_calculated_target(cls, user_id: int) -> None:
        """清除计算结果缓存"""
        key = cls.KEY_CALCULATED_TARGET.format(user_id=user_id)
        cache.delete(key)
    
    # ========== 股票元数据缓存 ==========
    
    @classmethod
    def get_stock_meta_all(cls) -> Optional[Dict]:
        """获取所有股票元数据缓存"""
        key = cls.KEY_STOCK_META_ALL
        return cache.get(key)
    
    @classmethod
    def set_stock_meta_all(cls, meta_dict: Dict) -> None:
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
    
    # ========== 股票实时价格缓存 ==========
    
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
            redis_client = get_redis_connection("default")
            
            # 构建完整的 Redis key（包含前缀和版本）
            keys = [f"stockmanager:1:stock:price:{code}" for code in code_list]
            
            # 使用 Pipeline 批量获取
            values = redis_client.mget(keys)
            
            # 反序列化
            result = {}
            for code, value in zip(code_list, values):
                if value:
                    result[code] = json.loads(value) if isinstance(value, (str, bytes)) else value
                else:
                    result[code] = None
            
            return result
        except Exception as e:
            logger.error(f"批量获取股价缓存失败: {e}")
            return {code: cls.get_stock_price(code) for code in code_list}
    
    @classmethod
    def set_stock_price(cls, code: str, price_data: Dict, ttl: int) -> None:
        """设置股票实时价格缓存"""
        key = cls.KEY_STOCK_PRICE.format(code=code)
        cache.set(key, price_data, ttl)
 
    
    @classmethod
    def get_stock_price_timestamp(cls) -> Optional[str]:
        """获取股票价格缓存时间戳"""
        key = cls.KEY_STOCK_PRICE_TIMESTAMP
        return cache.get(key)
    
    @classmethod
    def set_stock_price_timestamp(cls, timestamp: str) -> None:
        """设置股票价格缓存时间戳"""
        key = cls.KEY_STOCK_PRICE_TIMESTAMP
        cache.set(key, timestamp, cls.TTL_STOCK_PRICE_TRADING)
    
    @classmethod
    def clear_all_stock_prices(cls) -> None:
        """清除所有股票价格缓存"""
        try:
            redis_client = get_redis_connection("default")
            pattern = f"stockmanager:stock:price:*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"清除股票价格缓存失败: {e}")

