"""
Admin 基础配置模块
提供公共的导入和配置
"""
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.auth.models import User

from backend.common.auth_user import authenticated_user
from backend.models import Operation, Info, StockMeta, CashFlow


class BaseModelAdmin(admin.ModelAdmin):
    """全局 Admin 默认行为"""

    # 过滤器始终显示计数，去掉「显示计数 / 隐藏计数」切换
    show_facets = admin.ShowFacets.ALWAYS


class UserScopedModelAdmin(BaseModelAdmin):
    """按用户隔离数据的 ModelAdmin 基类"""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = authenticated_user(request)
        return qs if user.is_superuser else qs.filter(user=user)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is None or not isinstance(formfield.widget, RelatedFieldWidgetWrapper):
            return formfield

        # user：去掉添加/修改/查看/删除快捷图标
        if db_field.name == 'user':
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False
            formfield.widget.can_view_related = False
        # stock_meta：保留「+」以便先建 meta，关闭其余快捷图标
        elif db_field.name == 'stock_meta':
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False
            formfield.widget.can_view_related = False
        return formfield

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change=change, **kwargs)
        user = authenticated_user(request)
        if user.is_superuser and obj is None and 'user' in form.base_fields:
            form.base_fields['user'].initial = user
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not authenticated_user(request).is_superuser:
            readonly_fields.append('user')
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if authenticated_user(request).is_superuser or obj is not None:
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
            obj.user = authenticated_user(request)
        super().save_model(request, obj, form, change)

    def _owns_object(self, request, obj) -> bool:
        user = authenticated_user(request)
        return obj is None or user.is_superuser or obj.user == user

    def has_change_permission(self, request, obj=None):
        return self._owns_object(request, obj) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self._owns_object(request, obj) and super().has_delete_permission(request, obj)


__all__ = [
    'admin',
    'messages',
    'User',
    'Operation',
    'Info',
    'StockMeta',
    'CashFlow',
    'BaseModelAdmin',
    'UserScopedModelAdmin',
]
