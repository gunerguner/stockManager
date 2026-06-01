"""
股票操作记录管理
"""
from django.db.models import Max

from .base import Operation, StockMeta, UserScopedModelAdmin, admin, messages


@admin.register(Operation)
class OperationAdmin(UserScopedModelAdmin):
    """股票操作记录管理"""

    list_display = ['user', 'code', 'date', 'sortOrder', 'operationType', 'price', 'count', 'fee']
    list_filter = ['user', 'operationType', 'date']
    search_fields = ['code', 'user__username']
    date_hierarchy = 'date'
    ordering = ['-date', 'sortOrder', 'id']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'code', 'date', 'sortOrder', 'operationType')
        }),
        ('交易信息', {
            'fields': ('price', 'count', 'fee', 'comment')
        }),
        ('分红信息', {
            'fields': ('cash', 'stock', 'reserve'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user

        if not change and obj.sortOrder == 0:
            max_sort = Operation.objects.filter(
                user=obj.user,
                code=obj.code,
                date=obj.date,
            ).aggregate(Max('sortOrder'))['sortOrder__max']
            if max_sort is not None:
                obj.sortOrder = max_sort + 1

        if obj.code and obj.code.lower().startswith('hk'):
            messages.info(
                request,
                '港股通：price、fee 请按港币填写；除权除息请在 Admin 手动录入 DV。',
            )

        if obj.code and not StockMeta.objects.filter(code=obj.code).exists():
            messages.warning(
                request,
                f'⚠️ 提醒：股票代码 "{obj.code}" 在股票元数据（StockMeta）中不存在。'
                f'建议先在"股票元数据"中添加该股票的元信息，以便更好地管理。'
            )

        super().save_model(request, obj, form, change)
