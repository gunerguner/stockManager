"""底层缓存工具类"""
import json
from typing import Dict, List, Optional, Any

from django.core.cache import cache
from django_redis import get_redis_connection


class Cache:
    """底层缓存工具类，提供批量操作和模式删除"""
    
    @staticmethod
    def get_many(keys: List[str]) -> Dict[str, Optional[Any]]:
        """批量获取缓存（使用 Redis Pipeline 优化）"""
        if not keys:
            return {}
        
        try:
            redis_client = get_redis_connection("default")
            values = redis_client.mget(keys)
            
            result = {}
            for key, value in zip(keys, values):
                if value:
                    try:
                        result[key] = json.loads(value) if isinstance(value, (str, bytes)) else value
                    except (json.JSONDecodeError, TypeError):
                        result[key] = value
                else:
                    result[key] = None
            
            return result
        except Exception:
            return {key: cache.get(key) for key in keys}
    
    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """按模式删除缓存，返回删除的 key 数量"""
        try:
            redis_client = get_redis_connection("default")
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                return len(keys)
            return 0
        except Exception:
            return 0
