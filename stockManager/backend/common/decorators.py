"""
装饰器模块
提供视图装饰器功能
"""
import functools
import json
from typing import List
from .constants import ResponseStatus
from .middleware import json_response, get_client_ip

# 配置logger
import logging
logger = logging.getLogger(__name__)


def require_authentication(view_func):
    """
    装饰器：要求用户必须已认证
    
    使用方法:
        @require_authentication
        def my_view(request):
            # 视图逻辑
            pass
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return json_response(status=ResponseStatus.UNAUTHORIZED, message="未登录")
        return view_func(request, *args, **kwargs)
    return wrapper


def require_methods(methods):
    """
    装饰器：限制HTTP请求方法
    
    Args:
        methods: 允许的HTTP方法列表，如 ['GET', 'POST']
        
    使用方法:
        @require_methods(['POST'])
        def my_view(request):
            # 只接受POST请求
            pass
    """
    if isinstance(methods, str):
        methods = [methods]
    
    methods = [m.upper() for m in methods]
    
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                allowed = ', '.join(methods)
                return json_response(
                    status=ResponseStatus.ERROR,
                    message=f"不支持的请求方法，仅支持: {allowed}"
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_view_access(view_func):
    """
    装饰器：记录视图访问日志
    
    使用方法:
        @log_view_access
        def my_view(request):
            # 视图逻辑
            pass
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        ip = get_client_ip(request)
        user = request.user.username if request.user.is_authenticated else "匿名用户"
        logger.info(f"访问 {view_func.__name__} - 用户: {user}, IP: {ip}, 方法: {request.method}")
        
        try:
            response = view_func(request, *args, **kwargs)
            return response
        except Exception as e:
            logger.error(f"视图 {view_func.__name__} 执行异常: {str(e)}", exc_info=True)
            raise
            
    return wrapper


def handle_exception(view_func):
    """
    装饰器：统一处理异常和日志记录
    
    使用方法:
        @handle_exception
        def my_view(request):
            # 视图逻辑，不需要try-except
            pass
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"{view_func.__name__} 执行失败: {str(e)}", exc_info=True)
            return json_response(status=ResponseStatus.ERROR, message=f"{view_func.__name__}失败，请稍后重试")
    return wrapper


def parse_json_body(view_func):
    """
    装饰器：自动解析JSON请求体

    使用方法:
        @parse_json_body
        def my_view(request, data):
            # data是解析后的JSON数据
            pass
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 检查 Content-Type
        content_type = request.content_type or ''
        if 'application/json' not in content_type:
            logger.warning(f"{view_func.__name__} Content-Type错误: {content_type}")
            return json_response(status=ResponseStatus.ERROR, message="Content-Type 必须为 application/json")

        # 检查 body 是否为空
        if not request.body:
            logger.warning(f"{view_func.__name__} 请求体为空")
            return json_response(status=ResponseStatus.ERROR, message="请求体不能为空")

        try:
            data = json.loads(request.body)
            return view_func(request, data, *args, **kwargs)
        except json.JSONDecodeError as e:
            logger.error(f"{view_func.__name__} JSON解析失败: {e}")
            return json_response(status=ResponseStatus.ERROR, message="请求数据格式错误")
    return wrapper


def validate_required_fields(required_fields: List[str]):
    """
    装饰器工厂：验证必填字段
    
    Args:
        required_fields: 必填字段列表
        
    使用方法:
        @validate_required_fields(['username', 'password'])
        def my_view(request, data):
            # data已验证包含username和password
            pass
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, data, *args, **kwargs):
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return json_response(
                    status=ResponseStatus.ERROR,
                    message=f"缺少必填字段: {', '.join(missing_fields)}"
                )
            return view_func(request, data, *args, **kwargs)
        return wrapper
    return decorator
