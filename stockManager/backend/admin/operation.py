"""
股票操作记录管理
"""
from django.contrib import admin
from django.contrib import messages

from .base import Operation, StockMeta


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    """股票操作记录管理"""
    
    list_display = ['user', 'code', 'date', 'operationType', 'price', 'count', 'fee']
    list_filter = ['user', 'operationType', 'date']
    search_fields = ['code', 'user__username']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'code', 'date', 'operationType')
        }),
        ('交易信息', {
            'fields': ('price', 'count', 'fee', 'comment')
        }),
        ('分红信息', {
            'fields': ('cash', 'stock', 'reserve'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """普通用户只能看到自己的数据，超级用户可以看到所有数据"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
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
        """创建记录时自动关联当前用户，并检查StockMeta中是否存在该股票代码"""
        if not change:  # 新建时
            obj.user = request.user
        
        # 检查StockMeta中是否存在该股票代码
        if obj.code:
            stock_meta_exists = StockMeta.objects.filter(code=obj.code).exists()
            if not stock_meta_exists:
                # 使用warning级别显示提醒，不会阻止保存
                messages.warning(
                    request,
                    f'⚠️ 提醒：股票代码 "{obj.code}" 在股票元数据（StockMeta）中不存在。'
                    f'建议先在"股票元数据"中添加该股票的元信息，以便更好地管理。'
                )
        
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

