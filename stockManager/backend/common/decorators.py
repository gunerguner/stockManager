"""
装饰器模块
提供视图装饰器功能
"""
import functools
from .constants import STATUS_ERROR, STATUS_UNAUTHORIZED
from .responses import json_response
from .utils import get_client_ip

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
            return json_response(status=STATUS_UNAUTHORIZED, message="未登录")
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
                    status=STATUS_ERROR,
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

