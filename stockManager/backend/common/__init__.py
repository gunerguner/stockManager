"""
公共组件模块
提供装饰器、响应工具、常量等可复用组件
"""
from .constants import ResponseStatus, OperationType
from .decorators import (
    require_authentication,
    require_methods,
    log_view_access,
    handle_exception,
    parse_json_body,
    validate_required_fields,
)
from .middleware import json_response, get_client_ip
from .cache import Cache

# 配置logger
import logging
logger = logging.getLogger(__name__)

__all__ = [
    'ResponseStatus',
    'OperationType',
    'logger',
    'require_authentication',
    'require_methods',
    'log_view_access',
    'handle_exception',
    'parse_json_body',
    'validate_required_fields',
    'json_response',
    'get_client_ip',
    'Cache',
]

