"""
出入金记录管理
"""
from django.contrib import admin

from .base import CashFlow


@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
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
        if obj.amount >= 0:
            return f'+{obj.amount:.2f}'
        else:
            return f'{obj.amount:.2f}'
    formatted_amount.short_description = '金额'
    
    def transaction_type_display(self, obj):
        """交易类型显示"""
        if obj is None:
            return '-'
        return '入金' if obj.amount >= 0 else '出金'
    transaction_type_display.short_description = '类型'
    
    def get_queryset(self, request):
        """普通用户只能看到自己的数据，超级用户可以看到所有数据"""
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(user=request.user)
    
    def get_readonly_fields(self, request, obj=None):
        """普通用户编辑时 user 字段只读"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly_fields.append('user')
        return readonly_fields
    
    def get_fieldsets(self, request, obj=None):
        """普通用户创建时隐藏 user 字段"""
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser and obj is None:  # 普通用户创建新记录时
            # 移除 user 字段
            modified_fieldsets = []
            for name, options in fieldsets:
                fields = options.get('fields', [])
                if isinstance(fields, tuple):
                    fields = list(fields)
                if 'user' in fields:
                    fields = [f for f in fields if f != 'user']
                modified_fieldsets.append((name, {**options, 'fields': tuple(fields) if isinstance(options.get('fields'), tuple) else fields}))
            return modified_fieldsets
        return fieldsets
    
    def save_model(self, request, obj, form, change):
        """创建记录时自动关联当前用户"""
        if not change:  # 新建时
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        """普通用户只能修改自己的数据"""
        if obj is not None and not request.user.is_superuser:
            return obj.user == request.user
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """普通用户只能删除自己的数据"""
        if obj is not None and not request.user.is_superuser:
            return obj.user == request.user
        return super().has_delete_permission(request, obj)
