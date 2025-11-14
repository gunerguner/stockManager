"""
公共组件模块
提供装饰器、响应工具、常量等可复用组件
"""
from .constants import STATUS_SUCCESS, STATUS_ERROR, STATUS_UNAUTHORIZED
from .decorators import require_authentication, require_methods, log_view_access
from .responses import json_response
from .utils import get_client_ip, get_user_access_level

# 配置logger
import logging
logger = logging.getLogger(__name__)

__all__ = [
    'STATUS_SUCCESS',
    'STATUS_ERROR',
    'STATUS_UNAUTHORIZED',
    'logger',
    'require_authentication',
    'require_methods',
    'log_view_access',
    'json_response',
    'get_client_ip',
    'get_user_access_level',
]

