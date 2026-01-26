from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib import auth
from django.http import HttpRequest, JsonResponse

from ..common import (
    ResponseStatus,
    logger,
    require_authentication,
    json_response,
    require_methods,
    handle_exception,
    parse_json_body,
    validate_required_fields,
)


@csrf_exempt
@ensure_csrf_cookie
@require_methods(['POST'])
@parse_json_body
@validate_required_fields(['username', 'password'])
def login(request: HttpRequest, data: dict) -> JsonResponse:
    """用户登录接口"""
    if request.user.is_authenticated:
        return json_response(status=ResponseStatus.ERROR, message="已登录，请勿重复登录")
    
    username = data.get("username")
    password = data.get("password")
    
    user_obj = auth.authenticate(username=username, password=password)
    
    if user_obj is not None:
        auth.login(request, user_obj)
        logger.info(f"用户 {username} 登录成功")
        return json_response(status=ResponseStatus.SUCCESS, message="登录成功")
    else:
        logger.warning(f"用户 {username} 登录失败：用户名或密码错误")
        return json_response(status=ResponseStatus.ERROR, message="用户名或密码错误")


@require_authentication
@handle_exception
def logout(request: HttpRequest) -> JsonResponse:
    """用户登出接口"""
    username = request.user.username
    request.session.flush()
    logger.info(f"用户 {username} 登出成功")
    return json_response(status=ResponseStatus.SUCCESS, message="登出成功")


@ensure_csrf_cookie
@require_authentication
@handle_exception
def currentUser(request: HttpRequest) -> JsonResponse:
    """获取当前登录用户信息"""
    user = request.user
    if user.is_superuser:
        access = "admin"
    elif user.is_staff:
        access = "staff"
    else:
        access = ""
    
    user_info = {
        "username": user.username,
        "name": user.first_name,
        "avatar": "https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png",
        "access": access,
    }
    return json_response(status=ResponseStatus.SUCCESS, info=user_info)
