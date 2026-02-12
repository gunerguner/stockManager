"""股票元数据管理模块"""
from typing import Optional
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ..models import StockMeta as StockMetaModel
from .cacheRepository import CacheRepository
from ..common import logger


class StockMeta:
    """股票元数据管理器"""
    
    @classmethod
    def get(cls, code: str) -> Optional[StockMetaModel]:
        """根据股票代码获取 StockMeta"""
        return CacheRepository.get_stock_meta(code)


# 信号监听器
@receiver([post_save, post_delete], sender=StockMetaModel)
def refresh_stock_meta_cache(sender, instance, **kwargs):
    """监听模型变化，自动清除 Redis 缓存"""
    CacheRepository.clear_stock_meta_all()
    logger.info("清除股票元数据 Redis 缓存")
