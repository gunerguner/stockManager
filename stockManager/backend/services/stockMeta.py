"""股票元数据管理模块"""
from typing import Dict, Optional, ClassVar
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..models import StockMeta as StockMetaModel


class StockMeta:
    """股票元数据管理器"""
    _cache: ClassVar[Dict[str, StockMetaModel]] = {}
    
    @classmethod
    def get_dict(cls) -> Dict[str, StockMetaModel]:
        """获取 StockMeta 字典（懒加载）"""
        if not cls._cache:
            cls._cache = {meta.code: meta for meta in StockMetaModel.objects.all()}
        return cls._cache
    
    @classmethod
    def refresh(cls):
        """刷新缓存"""
        cls._cache = {meta.code: meta for meta in StockMetaModel.objects.all()}
    
    @classmethod
    def get(cls, code: str) -> Optional[StockMetaModel]:
        """根据股票代码获取 StockMeta"""
        return cls.get_dict().get(code)
    
    @classmethod
    def clear_cache(cls):
        """清空缓存"""
        cls._cache = {}


@receiver([post_save, post_delete], sender=StockMetaModel)
def refresh_stock_meta_cache(sender, instance, **kwargs):
    """监听模型变化，自动刷新缓存"""
    StockMeta.refresh()

