"""
出入金记录管理
"""
from .base import CashFlow, UserScopedModelAdmin, admin


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

    def formatted_amount(self, obj):
        """格式化金额显示"""
        if obj is None:
            return '-'
        return f'+{obj.amount:.2f}' if obj.amount >= 0 else f'{obj.amount:.2f}'
    formatted_amount.short_description = '金额'

    def transaction_type_display(self, obj):
        """交易类型显示"""
        if obj is None:
            return '-'
        return '入金' if obj.amount >= 0 else '出金'
    transaction_type_display.short_description = '类型'
