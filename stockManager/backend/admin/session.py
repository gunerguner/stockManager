"""
Session 管理
"""
import logging
from typing import Any

from django.contrib import messages
from django.contrib.sessions.models import Session
from django.db import transaction
from django.utils import timezone
from django.utils.html import format_html

from backend.admin.base import BaseModelAdmin, User, admin
from backend.common.auth_user import authenticated_user

# 取消 Django 默认的 Session 注册（如果已注册）
if Session in admin.site._registry:
    admin.site.unregister(Session)

logger = logging.getLogger(__name__)


@admin.register(Session)
class SessionAdmin(BaseModelAdmin):
    """Session 管理 - 仅超级管理员可见"""

    list_display = ['session_key', 'get_user', 'get_username', 'expire_date', 'is_expired']
    list_filter = ['expire_date']
    search_fields = ['session_key']
    readonly_fields = ['session_key', 'session_data', 'expire_date', 'get_user_info']
    ordering = ['-expire_date']
    actions = ['clear_selected_sessions', 'clear_expired_sessions', 'clear_all_sessions']

    def get_queryset(self, request):
        """只允许超级管理员访问"""
        qs = super().get_queryset(request)
        return qs if authenticated_user(request).is_superuser else qs.none()

    def has_module_permission(self, request):
        """控制是否在 admin 首页显示 Session 模块"""
        return authenticated_user(request).is_superuser

    def has_view_permission(self, request, obj=None):
        """控制是否有查看权限"""
        return authenticated_user(request).is_superuser

    def has_delete_permission(self, request, obj=None):
        """控制是否有删除权限"""
        return authenticated_user(request).is_superuser

    def has_add_permission(self, request):
        """不允许手动创建 session"""
        return False

    def has_change_permission(self, request, obj=None):
        """不允许修改 session"""
        return False

    def _get_user_from_session(self, obj: Session | None) -> User | None:
        """从 session 对象获取用户对象"""
        if obj is None:
            return None
        try:
            user_id = obj.get_decoded().get('_auth_user_id')
            if not user_id:
                return None
            return User.objects.get(pk=user_id)
        except Exception as e:
            logger.debug(f"解析 session 失败: {str(e)}")
            return None

    @admin.display(description='用户')
    def get_user(self, obj: Session) -> str:
        """获取 session 关联的用户（显示名称）"""
        user = self._get_user_from_session(obj)
        if user is None:
            return '匿名用户'
        return user.get_full_name() or user.email or user.username

    @admin.display(description='用户名')
    def get_username(self, obj: Session) -> str:
        """获取用户名（用于搜索和过滤）"""
        user = self._get_user_from_session(obj)
        return user.username if user else '-'

    @admin.display(description='用户信息')
    def get_user_info(self, obj: Session) -> Any:
        """获取用户详细信息（详情页显示）"""
        user = self._get_user_from_session(obj)
        if user is None:
            return '匿名用户（未登录）'

        return format_html(
            '用户名: {}<br>邮箱: {}<br>全名: {}<br>是否超级管理员: {}<br>是否员工: {}',
            user.username,
            user.email or '未设置',
            user.get_full_name() or '未设置',
            '是' if user.is_superuser else '否',
            '是' if user.is_staff else '否',
        )

    @admin.display(description='已过期', boolean=True)
    def is_expired(self, obj: Session | None) -> bool:
        """判断 session 是否过期"""
        if obj is None:
            return False
        try:
            return obj.expire_date < timezone.now()
        except Exception:
            return False

    def get_actions(self, request):
        """重写 get_actions 以移除默认的删除 action 并确保 allow_empty 生效"""
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)

        for action_name in ['clear_expired_sessions', 'clear_all_sessions']:
            action = actions.get(action_name)
            if action is None:
                continue
            func, name, description = action
            setattr(func, 'allow_empty', True)
            actions[action_name] = (func, name, description)

        return actions

    def _delete_and_notify(self, request, queryset, success_msg, empty_msg, msg_level=messages.SUCCESS):
        """通用删除和通知方法"""
        count = queryset.count()
        if count == 0:
            self.message_user(request, empty_msg, messages.INFO)
            return

        with transaction.atomic():
            queryset.delete()
        self.message_user(request, success_msg.format(count=count), msg_level)

    @admin.action(description='清理选中的 session')
    def clear_selected_sessions(self, request, queryset):
        """清理选中的 session"""
        if queryset.count() == 0:
            self.message_user(request, '请至少选择一个 session', messages.WARNING)
            return

        self._delete_and_notify(
            request,
            queryset,
            '成功清理 {count} 个 session',
            '没有选中的 session',
        )

    @admin.action(description='清理所有过期的 session')
    def clear_expired_sessions(self, request, queryset):
        """清理所有过期的 session（不需要选中项）"""
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        self._delete_and_notify(
            request,
            expired_sessions,
            '成功清理 {count} 个过期的 session',
            '当前没有过期的 session',
        )

    @admin.action(description='清理所有 session（所有用户将被登出）')
    def clear_all_sessions(self, request, queryset):
        """清理所有 session（危险操作，不需要选中项）"""
        all_sessions = Session.objects.all()
        self._delete_and_notify(
            request,
            all_sessions,
            '成功清理所有 {count} 个 session，所有用户将被登出',
            '当前没有 session',
            messages.WARNING,
        )


# Django Admin 支持无选中行仍执行的 action；stubs 未声明该属性，运行时 setattr 挂上。
setattr(SessionAdmin.clear_expired_sessions, 'allow_empty', True)
setattr(SessionAdmin.clear_all_sessions, 'allow_empty', True)
