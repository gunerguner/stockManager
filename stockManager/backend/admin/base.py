"""
Admin 基础配置模块
提供公共的导入和配置
"""
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth import get_user_model

from backend.models import Operation, Info, StockMeta, CashFlow

User = get_user_model()


class UserScopedModelAdmin(admin.ModelAdmin):
    """按用户隔离数据的 ModelAdmin 基类"""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(user=request.user)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.is_superuser and obj is None and 'user' in form.base_fields:
            form.base_fields['user'].initial = request.user
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly_fields.append('user')
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser or obj is not None:
            return fieldsets

        modified_fieldsets = []
        for name, options in fieldsets:
            fields = list(options.get('fields', []))
            if 'user' in fields:
                fields = [field for field in fields if field != 'user']
            modified_fieldsets.append((name, {**options, 'fields': tuple(fields)}))
        return modified_fieldsets

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def _owns_object(self, request, obj) -> bool:
        return obj is None or request.user.is_superuser or obj.user == request.user

    def has_change_permission(self, request, obj=None):
        return self._owns_object(request, obj) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self._owns_object(request, obj) and super().has_delete_permission(request, obj)


__all__ = ['admin', 'messages', 'User', 'Operation', 'Info', 'StockMeta', 'CashFlow', 'UserScopedModelAdmin']
