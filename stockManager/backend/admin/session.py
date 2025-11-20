"""
Session 管理
"""
import logging

from django.contrib import admin
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.html import format_html
from django.db import transaction

from .base import User

# 取消 Django 默认的 Session 注册（如果已注册）
if Session in admin.site._registry:
    admin.site.unregister(Session)

logger = logging.getLogger(__name__)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Session 管理 - 仅超级管理员可见"""
    
    list_display = ['session_key', 'get_user', 'get_username', 'expire_date', 'is_expired']
    list_filter = ['expire_date']
    search_fields = ['session_key']
    readonly_fields = ['session_key', 'session_data', 'expire_date', 'get_user_info']
    ordering = ['-expire_date']
    
    def get_queryset(self, request):
        """只允许超级管理员访问"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.none()
        return qs
    
    def has_module_permission(self, request):
        """控制是否在 admin 首页显示 Session 模块"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """控制是否有查看权限"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """控制是否有删除权限"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """不允许手动创建 session"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """不允许修改 session"""
        return False
    
    def get_user(self, obj):
        """获取 session 关联的用户（显示名称）"""
        if obj is None:
            return '-'
        try:
            session_data = obj.get_decoded()
            user_id = session_data.get('_auth_user_id')
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    display_name = user.get_full_name() or user.email or user.username
                    return display_name
                except User.DoesNotExist:
                    return f"用户ID: {user_id} (已删除)"
            return '匿名用户'
        except Exception as e:
            # 记录异常但不抛出，避免影响页面显示
            logger.debug(f"解析 session 失败: {str(e)}")
            return '解析失败'
    get_user.short_description = '用户'
    
    def get_username(self, obj):
        """获取用户名（用于搜索和过滤）"""
        if obj is None:
            return '-'
        try:
            session_data = obj.get_decoded()
            user_id = session_data.get('_auth_user_id')
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    return user.username
                except User.DoesNotExist:
                    return f"ID:{user_id}"
            return '-'
        except Exception as e:
            logger.debug(f"解析 session 用户名失败: {str(e)}")
            return '-'
    get_username.short_description = '用户名'
    
    def get_user_info(self, obj):
        """获取用户详细信息（详情页显示）"""
        if obj is None:
            return '-'
        try:
            session_data = obj.get_decoded()
            user_id = session_data.get('_auth_user_id')
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    return format_html(
                        '用户名: {}<br>邮箱: {}<br>全名: {}<br>是否超级管理员: {}<br>是否员工: {}',
                        user.username,
                        user.email or '未设置',
                        user.get_full_name() or '未设置',
                        '是' if user.is_superuser else '否',
                        '是' if user.is_staff else '否'
                    )
                except User.DoesNotExist:
                    return f"用户ID: {user_id} (用户已被删除)"
            return '匿名用户（未登录）'
        except Exception as e:
            logger.debug(f"解析 session 用户信息失败: {str(e)}")
            return f'解析失败: {str(e)}'
    get_user_info.short_description = '用户信息'
    
    def is_expired(self, obj):
        """判断 session 是否过期"""
        if obj is None:
            return False
        try:
            return obj.expire_date < timezone.now()
        except Exception:
            return False
    is_expired.boolean = True
    is_expired.short_description = '已过期'
    
    # 注意：clear_expired_sessions 和 clear_all_sessions 不需要选中项
    # 但 Django admin 默认要求至少选中一项，所以我们需要在函数中处理空 queryset
    actions = ['clear_selected_sessions', 'clear_expired_sessions', 'clear_all_sessions']
    
    def get_actions(self, request):
        """重写 get_actions 以移除默认的删除 action 并确保 allow_empty 生效"""
        actions = super().get_actions(request)
        
        # 移除默认的删除 action
        if 'delete_selected' in actions:
            del actions['delete_selected']
        
        for action_name in ['clear_expired_sessions', 'clear_all_sessions']:
            if action_name in actions:
                func, name, description = actions[action_name]
                # 强制设置 allow_empty 属性
                func.allow_empty = True
                # 重新组装 actions 字典
                actions[action_name] = (func, name, description)
        
        return actions
    
    def clear_selected_sessions(self, request, queryset):
        """清理选中的 session"""
        if queryset.count() == 0:
            self.message_user(
                request,
                '请至少选择一个 session',
                messages.WARNING
            )
            return
        
        count = queryset.count()
        with transaction.atomic():
            queryset.delete()
        self.message_user(
            request,
            f'成功清理 {count} 个 session',
            messages.SUCCESS
        )
    clear_selected_sessions.short_description = '清理选中的 session'
    
    def clear_expired_sessions(self, request, queryset):
        """清理所有过期的 session（不需要选中项）"""
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        count = expired_sessions.count()
        
        if count == 0:
            self.message_user(
                request,
                '当前没有过期的 session',
                messages.INFO
            )
            return
        
        with transaction.atomic():
            expired_sessions.delete()
        self.message_user(
            request,
            f'成功清理 {count} 个过期的 session',
            messages.SUCCESS
        )
    clear_expired_sessions.short_description = '清理所有过期的 session'
    clear_expired_sessions.allow_empty = True
    
    def clear_all_sessions(self, request, queryset):
        """清理所有 session（危险操作，不需要选中项）"""
        count = Session.objects.count()
        
        if count == 0:
            self.message_user(
                request,
                '当前没有 session',
                messages.INFO
            )
            return
        
        with transaction.atomic():
            Session.objects.all().delete()
        self.message_user(
            request,
            f'成功清理所有 {count} 个 session，所有用户将被登出',
            messages.WARNING
        )
    clear_all_sessions.short_description = '清理所有 session（所有用户将被登出）'
    clear_all_sessions.allow_empty = True

