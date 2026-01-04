"""股票元数据管理模块"""
from typing import Dict, Optional
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ..models import StockMeta as StockMetaModel
from .cacheManager import CacheManager
from ..common import logger


class StockMeta:
    """股票元数据管理器（使用 Redis 缓存）"""
    
    @classmethod
    def get_dict(cls) -> Dict[str, StockMetaModel]:
        """获取 StockMeta 字典（带 Redis 缓存）"""
        # 尝试从 Redis 获取
        cached_data = CacheManager.get_stock_meta_all()
        if cached_data:
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
        meta_dict = {meta.code: meta for meta in StockMetaModel.objects.all()}
        
        # 写入 Redis 缓存
        CacheManager.set_stock_meta_all(meta_dict)
        
        return meta_dict
    
    @classmethod
    def get(cls, code: str) -> Optional[StockMetaModel]:
        """根据股票代码获取 StockMeta"""
        return cls.get_dict().get(code)
    
    @classmethod
    def clear_cache(cls):
        """清空 Redis 缓存"""
        CacheManager.clear_stock_meta_all()


# 信号监听器
@receiver([post_save, post_delete], sender=StockMetaModel)
def refresh_stock_meta_cache(sender, instance, **kwargs):
    """监听模型变化，自动清除 Redis 缓存"""
    StockMeta.clear_cache()
    logger.info("清除股票元数据 Redis 缓存")

