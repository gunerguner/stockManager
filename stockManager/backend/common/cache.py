"""底层缓存工具类"""
from typing import Dict, List, Optional, Any

from django.core.cache import cache
from django_redis import get_redis_connection


class Cache:
    """底层缓存工具类，提供批量操作和模式删除"""

    @staticmethod
    def make_key(key: str, version: int = None) -> str:
        """逻辑 key -> Redis 完整 key（与 cache.get/set 一致的前缀与版本）"""
        return cache.make_key(key, version=version)

    @staticmethod
    def make_pattern(pattern: str, version: int = None) -> str:
        """逻辑通配 pattern -> Redis 完整 pattern"""
        return cache.make_key('', version=version) + pattern

    @staticmethod
    def get_many(keys: List[str]) -> Dict[str, Optional[Any]]:
        """批量获取缓存；keys 为逻辑 key（不含 KEY_PREFIX/VERSION）"""
        if not keys:
            return {}

        full_keys = [cache.make_key(k) for k in keys]

        try:
            redis_client = get_redis_connection("default")
            client = cache.client
            values = redis_client.mget(full_keys)

            result = {}
            for logical_key, raw in zip(keys, values):
                result[logical_key] = client.decode(raw) if raw is not None else None

            return result
        except Exception:
            return {key: cache.get(key) for key in keys}

    @staticmethod
    def set_many(mapping: Dict[str, Any], timeout: int = None) -> None:
        """批量设置缓存；mapping 的 key 为逻辑 key，序列化/前缀与 cache.set 一致"""
        if not mapping:
            return

        try:
            redis_client = get_redis_connection("default")
            client = cache.client
            pipe = redis_client.pipeline()
            for logical_key, value in mapping.items():
                if value is not None:
                    client.set(logical_key, value, timeout, client=pipe)
            pipe.execute()
        except Exception:
            for logical_key, value in mapping.items():
                if value is not None:
                    cache.set(logical_key, value, timeout)

    @staticmethod
    def delete_pattern(pattern: str, *, logical: bool = True) -> int:
        """按模式删除缓存，返回删除的 key 数量；默认 pattern 为逻辑通配符"""
        if logical:
            pattern = Cache.make_pattern(pattern)
        try:
            redis_client = get_redis_connection("default")
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                return len(keys)
            return 0
        except Exception:
            return 0
