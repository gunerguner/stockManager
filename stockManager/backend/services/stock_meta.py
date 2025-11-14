"""
股票元数据管理模块
全局管理 StockMeta 数据，提供缓存和查询功能
"""
from typing import Dict, Optional

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ..models import StockMeta as StockMetaModel


class StockMeta:
    """股票元数据管理器（全局单例模式）"""
    
    _instance = None
    _cache: Dict[str, StockMetaModel] = None
    
    def __new__(cls):
        """单例模式，确保全局只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_dict(self) -> Dict[str, StockMetaModel]:
        """
        获取 StockMeta 字典（懒加载，首次访问时加载）
        
        Returns:
            Dict[str, StockMetaModel]: 股票代码到 StockMeta 的映射字典
        """
        if self._cache is None:
            self._cache = {meta.code: meta for meta in StockMetaModel.objects.all()}
        return self._cache
    
    def refresh(self):
        """刷新 StockMeta 缓存"""
        self._cache = {meta.code: meta for meta in StockMetaModel.objects.all()}
    
    def get(self, code: str) -> Optional[StockMetaModel]:
        """
        根据股票代码获取 StockMeta
        
        Args:
            code: 股票代码
            
        Returns:
            StockMetaModel 对象，如果不存在则返回 None
        """
        return self.get_dict().get(code)
    
    def clear_cache(self):
        """清空缓存（下次访问时会重新加载）"""
        self._cache = None


@receiver([post_save, post_delete], sender=StockMetaModel)
def refresh_stock_meta_cache(sender, instance, **kwargs):
    """
    监听 StockMeta 模型保存和删除信号，自动刷新缓存
    
    Args:
        sender: 发送信号的模型类
        instance: 模型实例
        **kwargs: 其他参数
    """
    StockMeta().refresh()

