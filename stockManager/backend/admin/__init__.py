"""
Django Admin 配置模块
统一导入所有 admin 配置类，确保所有 admin 类被注册
"""
# 导入所有 admin 配置类，触发 @admin.register 装饰器
from . import operation  # noqa: F401
from . import info  # noqa: F401
from . import cashflow  # noqa: F401
from . import stockmeta  # noqa: F401
from . import session  # noqa: F401

__all__ = [
    'operation',
    'info',
    'cashflow',
    'stockmeta',
    'session',
]

