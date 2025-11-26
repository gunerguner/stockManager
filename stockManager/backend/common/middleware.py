"""
中间件工具模块
提供统一的JSON响应格式和HTTP请求处理工具
"""
from typing import Optional, Any
from django.http import JsonResponse, HttpRequest

from .constants import ResponseStatus


def json_response(
    status: ResponseStatus, 
    message: Optional[str] = None, 
    data: Optional[Any] = None, 
    **kwargs
) -> JsonResponse:
    """
    统一的JSON响应格式
    
    Args:
        status: 响应状态码，必须是 ResponseStatus 枚举
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


def get_client_ip(request: HttpRequest) -> str:
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

