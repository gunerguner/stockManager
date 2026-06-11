"""关注列表管理"""
from backend.models import WatchItem
from backend.admin.base import UserScopedModelAdmin, admin


@admin.register(WatchItem)
class WatchItemAdmin(UserScopedModelAdmin):
    """关注列表"""

    list_display = ['user', 'code', 'leftPoint', 'trendPoint', 'bloodPoint']
    list_filter = ['user']
    search_fields = ['code']
    ordering = ['user', 'id']
    fieldsets = (
        ('基本信息', {'fields': ('user', 'code')}),
        ('主观判断', {'fields': ('risk', 'opportunity'), 'classes': ('wide',)}),
        ('买点', {'fields': ('leftPoint', 'trendPoint', 'bloodPoint')}),
    )
