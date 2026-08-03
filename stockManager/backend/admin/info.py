"""
用户资金信息管理
"""
from django.contrib import messages

from backend.admin.base import Info, UserScopedModelAdmin, admin
from backend.admin.constants import NAV_REFRESH_HINT


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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.info_type == Info.InfoType.INCOME_CASH:
            messages.warning(request, NAV_REFRESH_HINT)

    def delete_model(self, request, obj):
        is_income = obj.info_type == Info.InfoType.INCOME_CASH
        super().delete_model(request, obj)
        if is_income:
            messages.warning(request, NAV_REFRESH_HINT)

    def delete_queryset(self, request, queryset):
        has_income = queryset.filter(info_type=Info.InfoType.INCOME_CASH).exists()
        super().delete_queryset(request, queryset)
        if has_income:
            messages.warning(request, NAV_REFRESH_HINT)
