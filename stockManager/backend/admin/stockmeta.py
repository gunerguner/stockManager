"""
股票元数据管理
"""
from django.contrib import admin

from .base import StockMeta

@admin.register(StockMeta)
class StockMetaAdmin(admin.ModelAdmin):
    """股票元数据管理（全局共享）"""
    
    list_display = ['code', 'stockType', 'isNew']
    list_filter = ['stockType', 'isNew']
    search_fields = ['code']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'stockType', 'isNew')
        }),
    )
    # StockMeta 是全局共享的，所有用户都可以看到和操作