"""关注列表管理"""
from backend.models import WatchItem
from backend.admin.base import UserScopedModelAdmin, admin


@admin.register(WatchItem)
class WatchItemAdmin(UserScopedModelAdmin):
    """关注列表"""

    list_display = ['user', 'stock_name', 'hidden', 'leftPoint', 'trendPoint', 'bloodPoint']
    list_filter = ['user', 'hidden']
    search_fields = ['stock_meta__code', 'stock_meta__name']
    autocomplete_fields = ['stock_meta']
    list_select_related = ('stock_meta',)
    ordering = ['user', 'id']
    fieldsets = (
        ('基本信息', {'fields': ('user', 'stock_meta', 'hidden')}),
        ('主观判断', {'fields': ('risk', 'opportunity'), 'classes': ('wide',)}),
        ('买点', {'fields': ('leftPoint', 'trendPoint', 'bloodPoint')}),
    )

    @admin.display(description='股票', ordering='stock_meta__name')
    def stock_name(self, obj: WatchItem) -> str:
        meta = obj.stock_meta
        return (meta.name or meta.code) if meta else '-'
