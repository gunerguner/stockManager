"""
股票元数据管理
"""
from backend.admin.base import BaseModelAdmin, StockMeta, admin


@admin.register(StockMeta)
class StockMetaAdmin(BaseModelAdmin):
    """股票元数据管理（全局共享）"""

    list_display = ['code', 'name', 'stockType', 'isNew']
    list_filter = ['stockType', 'isNew']
    search_fields = ['code', 'name']

    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'name', 'stockType', 'isNew')
        }),
    )
    # StockMeta 是全局共享的，所有用户都可以看到和操作