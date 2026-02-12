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
    def set_many(mapping: Dict[str, Any], timeout: int = None) -> None:
        """批量设置缓存（使用 Redis Pipeline 优化）"""
        if not mapping:
            return

        try:
            redis_client = get_redis_connection("default")
            pipe = redis_client.pipeline()

            for key, value in mapping.items():
                if value is not None:
                    # 如果是复杂对象，先序列化
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    pipe.set(key, value, ex=timeout)

            pipe.execute()
        except Exception as e:
            # 如果批量设置失败，回退到单条设置
            for key, value in mapping.items():
                if value is not None:
                    try:
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value)
                        cache.set(key, value, timeout)
                    except Exception:
                        # 如果序列化失败，直接设置原始值
                        cache.set(key, value, timeout)

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
