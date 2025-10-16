"""
Django视图通用组件模块
包含装饰器、日志配置、通用函数等可复用组件
"""
from django.http import JsonResponse
import logging
import functools

# 状态码常量
STATUS_SUCCESS = 1  # 操作成功
STATUS_ERROR = 0  # 操作失败
STATUS_UNAUTHORIZED = 302  # 未登录/未授权

# 配置logger
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
            return JsonResponse({"status": STATUS_UNAUTHORIZED, "message": "未登录"})
        return view_func(request, *args, **kwargs)
    return wrapper

def get_user_access_level(user):
    """
    获取用户访问权限级别
    
    Args:
        user: Django User对象
        
    Returns:
        str: 权限级别 - "admin"(超级管理员) / "staff"(员工) / ""(普通用户)
    """
    if user.is_superuser:
        return "admin"
    elif user.is_staff:
        return "staff"
    return ""


def get_client_ip(request):
    """
    获取请求客户端的真实IP地址
    支持代理服务器场景
    
    Args:
        request: Django request对象
        
    Returns:
        str: 客户端IP地址
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # 使用代理时获取真实IP（取第一个）
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        # 未使用代理时直接获取
        ip = request.META.get('REMOTE_ADDR')
    return ip


def json_response(status, message=None, data=None, **kwargs):
    """
    统一的JSON响应格式
    
    Args:
        status: 响应状态码 (1: 成功, 0: 失败, 302: 未登录等)
        message: 响应消息
        data: 响应数据
        **kwargs: 其他需要添加到响应中的字段
        
    Returns:
        JsonResponse对象
    """
    response_data = {"status": status}
    
    if message is not None:
        response_data["message"] = message
        
    if data is not None:
        response_data["data"] = data
        
    # 添加其他自定义字段
    response_data.update(kwargs)
    
    return JsonResponse(response_data, safe=False)


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

