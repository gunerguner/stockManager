"""
用户资金信息管理
"""
from .base import Info, UserScopedModelAdmin, admin


@admin.register(Info)
class InfoAdmin(UserScopedModelAdmin):
    """用户资金信息管理"""

    list_display = ['user', 'info_type', 'value']
    list_filter = ['user', 'info_type']
    search_fields = ['user__username']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'info_type', 'value')
        }),
    )
