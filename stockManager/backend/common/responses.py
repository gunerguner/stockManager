"""
响应工具模块
提供统一的JSON响应格式
"""
from django.http import JsonResponse


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

