"""
公共工具函数模块
"""
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

