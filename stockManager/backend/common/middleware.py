"""中间件工具模块"""
from typing import Optional, Any
from django.http import JsonResponse, HttpRequest
from .constants import ResponseStatus


def json_response(status: ResponseStatus, message: Optional[str] = None, data: Optional[Any] = None, **kwargs) -> JsonResponse:
    """统一的JSON响应格式"""
    response_data = {"status": status}

    if message is not None:
        response_data["message"] = message
    if data is not None:
        response_data["data"] = data
        
    response_data.update(kwargs)
    return JsonResponse(response_data, safe=False)


def get_client_ip(request: HttpRequest) -> str:
    """获取请求客户端的真实IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR', '')
