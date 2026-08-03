"""HTTP 关注点：认证、响应、视图装饰器"""
from backend.common.web.auth_user import authenticated_user
from backend.common.web.decorators import (
    handle_exception,
    parse_json_body,
    require_authentication,
    require_methods,
    require_superuser,
    validate_required_fields,
)
from backend.common.web.response import get_client_ip, json_response

__all__ = [
    'authenticated_user',
    'get_client_ip',
    'handle_exception',
    'json_response',
    'parse_json_body',
    'require_authentication',
    'require_methods',
    'require_superuser',
    'validate_required_fields',
]
