from django.contrib import admin

from .models import Operation, Info, StockMeta


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


@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    """用户资金信息管理"""
    
    list_display = ['user', 'info_type', 'value']
    list_filter = ['user', 'info_type']
    search_fields = ['user__username']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'info_type', 'value')
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


@admin.register(StockMeta)
class StockMetaAdmin(admin.ModelAdmin):
    """股票元数据管理（全局共享）"""
    
    list_display = ['code', 'stockType', 'isNew']
    list_filter = ['stockType', 'isNew']
    search_fields = ['code']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'stockType', 'isNew')
        }),
    )
    
    # StockMeta 是全局共享的，所有用户都可以看到和操作