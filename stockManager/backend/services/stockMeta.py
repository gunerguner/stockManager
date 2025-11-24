"""
股票元数据管理模块
全局管理 StockMeta 数据，提供缓存和查询功能
"""
from typing import Dict, Optional, ClassVar

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ..models import StockMeta as StockMetaModel


class StockMeta:
    """股票元数据管理器（使用类方法和类变量）"""
    
    # 类变量：缓存字典
    _cache: ClassVar[Dict[str, StockMetaModel]] = {}
    
    @classmethod
    def get_dict(cls) -> Dict[str, StockMetaModel]:
        """
        获取 StockMeta 字典（懒加载，首次访问时加载）
        
        Returns:
            Dict[str, StockMetaModel]: 股票代码到 StockMeta 的映射字典
        """
        if not cls._cache:
            cls._cache = {meta.code: meta for meta in StockMetaModel.objects.all()}
        return cls._cache
    
    @classmethod
    def refresh(cls):
        """刷新 StockMeta 缓存"""
        cls._cache = {meta.code: meta for meta in StockMetaModel.objects.all()}
    
    @classmethod
    def get(cls, code: str) -> Optional[StockMetaModel]:
        """
        根据股票代码获取 StockMeta
        
        Args:
            code: 股票代码
            
        Returns:
            StockMetaModel 对象，如果不存在则返回 None
        """
        return cls.get_dict().get(code)
    
    @classmethod
    def clear_cache(cls):
        """清空缓存（下次访问时会重新加载）"""
        cls._cache = {}


@receiver([post_save, post_delete], sender=StockMetaModel)
def refresh_stock_meta_cache(sender, instance, **kwargs):
    """
    监听 StockMeta 模型保存和删除信号，自动刷新缓存
    
    Args:
        sender: 发送信号的模型类
        instance: 模型实例
        **kwargs: 其他参数
    """
    StockMeta.refresh()

