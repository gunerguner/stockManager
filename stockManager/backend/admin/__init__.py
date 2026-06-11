"""
Django Admin 配置模块
统一导入所有 admin 配置类，确保所有 admin 类被注册
"""
# 导入所有 admin 配置类，触发 @admin.register 装饰器
from backend.admin import operation  # noqa: F401
from backend.admin import info  # noqa: F401
from backend.admin import cashflow  # noqa: F401
from backend.admin import stockmeta  # noqa: F401
from backend.admin import session  # noqa: F401
from backend.admin import watchitem  # noqa: F401

__all__ = [
    'operation',
    'info',
    'cashflow',
    'stockmeta',
    'session',
    'watchitem',
]

