"""
公共组件模块
提供装饰器、响应工具、常量等可复用组件
"""
from backend.common.constants import ResponseStatus, OperationType
from backend.common.decorators import (
    require_authentication,
    require_superuser,
    require_methods,
    handle_exception,
    parse_json_body,
    validate_required_fields,
)
from backend.common.middleware import json_response, get_client_ip
from backend.common.cache import Cache

# 配置logger
import logging
logger = logging.getLogger(__name__)

__all__ = [
    'ResponseStatus',
    'OperationType',
    'logger',
    'require_authentication',
    'require_superuser',
    'require_methods',
    'handle_exception',
    'parse_json_body',
    'validate_required_fields',
    'json_response',
    'get_client_ip',
    'Cache',
]

