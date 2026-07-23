"""
股票操作记录管理
"""
from django.db.models import Max

from backend.common.market import is_hk_code
from backend.admin.base import Operation, UserScopedModelAdmin, admin, messages


@admin.register(Operation)
class OperationAdmin(UserScopedModelAdmin):
    """股票操作记录管理"""

    list_display = ['user', 'stock_name', 'date', 'sortOrder', 'operationType', 'price', 'count', 'fee']
    list_filter = ['user', 'operationType', 'date']
    search_fields = ['stock_meta__code', 'stock_meta__name', 'user__username']
    autocomplete_fields = ['stock_meta']
    list_select_related = ('stock_meta',)
    date_hierarchy = 'date'
    ordering = ['-date', 'sortOrder', 'id']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'stock_meta', 'date', 'sortOrder', 'operationType')
        }),
        ('交易信息', {
            'fields': ('price', 'count', 'fee', 'comment')
        }),
        ('分红信息', {
            'fields': ('cash', 'stock', 'reserve'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='股票', ordering='stock_meta__name')
    def stock_name(self, obj):
        meta = obj.stock_meta
        return (meta.name or meta.code) if meta else '-'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        if not change and obj.sortOrder == 0:
            max_sort = Operation.objects.filter(
                user=obj.user,
                stock_meta=obj.stock_meta,
                date=obj.date,
            ).aggregate(Max('sortOrder'))['sortOrder__max']
            if max_sort is not None:
                obj.sortOrder = max_sort + 1

        if obj.stock_meta_id and is_hk_code(obj.code):
            messages.info(
                request,
                '港股通：price、fee 请按港币填写；除权除息请在 Admin 手动录入 DV。',
            )

        super().save_model(request, obj, form, change)
