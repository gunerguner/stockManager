"""
出入金记录管理
"""
from django.contrib import messages

from backend.admin.base import CashFlow, UserScopedModelAdmin, admin

_NAV_REFRESH_HINT = (
    '净值数据可能已过期，请到「净值分析」页刷新；'
    '若修改了历史交易或出入金，请使用全量刷新。'
)


@admin.register(CashFlow)
class CashFlowAdmin(UserScopedModelAdmin):
    """出入金记录管理（金额正数为入金，负数为出金）"""

    list_display = ['user', 'transaction_date', 'formatted_amount', 'transaction_type_display']
    list_filter = ['user', 'transaction_date']
    search_fields = ['user__username']
    date_hierarchy = 'transaction_date'
    ordering = ['-transaction_date']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'transaction_date', 'amount')
        }),
    )

    @admin.display(description='金额')
    def formatted_amount(self, obj: CashFlow | None) -> str:
        """格式化金额显示"""
        if obj is None:
            return '-'
        return f'+{obj.amount:.2f}' if obj.amount >= 0 else f'{obj.amount:.2f}'

    @admin.display(description='类型')
    def transaction_type_display(self, obj: CashFlow | None) -> str:
        """交易类型显示"""
        if obj is None:
            return '-'
        return '入金' if obj.amount >= 0 else '出金'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.warning(request, _NAV_REFRESH_HINT)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        messages.warning(request, _NAV_REFRESH_HINT)

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        messages.warning(request, _NAV_REFRESH_HINT)
