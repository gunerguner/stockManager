"""
股票操作记录管理
"""
from django import forms
from django.contrib import messages
from django.db.models import Max

from backend.admin.base import Operation, UserScopedModelAdmin, admin
from backend.common.auth_user import authenticated_user
from backend.common.constants import OperationType
from backend.common.market import is_hk_code
from backend.services.cache.fx_store import get_hkd_cny_rate


class OperationAdminForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        if not cleaned:
            return cleaned

        stock_meta = cleaned.get('stock_meta')
        op_type = cleaned.get('operationType')
        amount = cleaned.get('amount')
        price = cleaned.get('price') or 0
        count = cleaned.get('count') or 0

        if not stock_meta or op_type not in (OperationType.BUY, OperationType.SELL):
            return cleaned

        code = stock_meta.code
        if not is_hk_code(code):
            cleaned['amount'] = None
            return cleaned

        if amount is None or amount <= 0:
            try:
                rate = get_hkd_cny_rate([code])
                cleaned['amount'] = price * count * rate
            except Exception as exc:
                raise forms.ValidationError(
                    '港股通买卖必须填写成交金额（人民币），且大于 0'
                ) from exc

        if cleaned.get('amount') is None or cleaned['amount'] <= 0:
            raise forms.ValidationError(
                '港股通买卖必须填写成交金额（人民币），且大于 0'
            )
        return cleaned


@admin.register(Operation)
class OperationAdmin(UserScopedModelAdmin):
    """股票操作记录管理"""

    form = OperationAdminForm
    list_display = [
        'user', 'stock_name', 'date', 'sortOrder', 'operationType',
        'price', 'count', 'amount', 'fee',
    ]
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
            'fields': ('price', 'count', 'amount', 'fee', 'comment'),
            'description': (
                '港股通：价格填港币；成交金额、佣金填人民币。'
                '非港股：成交金额留空，价格与佣金填人民币。'
            ),
        }),
        ('分红信息', {
            'fields': ('cash', 'stock', 'reserve'),
            'classes': ('collapse',),
            'description': (
                '除权除息请手动录入操作类型为「除权除息」。'
                '港股通分红按人民币到账填写。'
            ),
        }),
    )

    @admin.display(description='股票', ordering='stock_meta__name')
    def stock_name(self, obj: Operation) -> str:
        meta = obj.stock_meta
        return (meta.name or meta.code) if meta else '-'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = authenticated_user(request)
        if not change and obj.sortOrder == 0:
            max_sort = Operation.objects.filter(
                user=obj.user,
                stock_meta=obj.stock_meta,
                date=obj.date,
            ).aggregate(Max('sortOrder'))['sortOrder__max']
            if max_sort is not None:
                obj.sortOrder = max_sort + 1

        if obj.stock_meta_id and is_hk_code(obj.code):
            if obj.operationType in (OperationType.BUY, OperationType.SELL):
                messages.info(
                    request,
                    '港股通：价格为港币，成交金额与佣金为人民币。',
                )

        super().save_model(request, obj, form, change)
