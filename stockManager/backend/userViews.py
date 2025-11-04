from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib import auth

import json

# 导入公共组件
from .common import (
    STATUS_SUCCESS,
    STATUS_ERROR,
    logger,
    require_authentication,
    get_user_access_level,
    json_response,
    require_methods,
)


@csrf_exempt
@ensure_csrf_cookie
@require_methods(['POST'])
def login(request):
    """用户登录接口"""
    # 不允许重复登录
    if request.user.is_authenticated:
        return json_response(status=STATUS_ERROR, message="已登录，请勿重复登录")
    
    try:
        # 一次性解析请求体
        request_data = json.loads(request.body)
        username = request_data.get("username")
        password = request_data.get("password")
        
        # 验证必填字段
        if not username or not password:
            return json_response(status=STATUS_ERROR, message="用户名和密码不能为空")
        
        # 认证用户
        user_obj = auth.authenticate(username=username, password=password)
        
        if user_obj is not None:
            auth.login(request, user_obj)
            logger.info(f"用户 {username} 登录成功")
            return json_response(status=STATUS_SUCCESS, message="登录成功")
        else:
            logger.warning(f"用户 {username} 登录失败：用户名或密码错误")
            return json_response(status=STATUS_ERROR, message="用户名或密码错误")
            
    except json.JSONDecodeError:
        logger.error("登录请求JSON解析失败")
        return json_response(status=STATUS_ERROR, message="请求数据格式错误")
    except Exception as e:
        logger.error(f"登录过程发生异常: {str(e)}")
        return json_response(status=STATUS_ERROR, message="登录失败，请稍后重试")

@require_authentication
def logout(request):
    """用户登出接口"""
    try:
        username = request.user.username
        request.session.flush()
        logger.info(f"用户 {username} 登出成功")
        return json_response(status=STATUS_SUCCESS, message="登出成功")
    except Exception as e:
        logger.error(f"登出过程发生异常: {str(e)}")
        return json_response(status=STATUS_ERROR, message="登出失败")



@ensure_csrf_cookie
@require_authentication
def currentUser(request):
    """获取当前登录用户信息"""
    try:
        user = request.user
        user_info = {
            "username": user.username,
            "name": user.first_name,
            "avatar": "https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png",
            "access": get_user_access_level(user),
        }
        return json_response(status=STATUS_SUCCESS, info=user_info)
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return json_response(status=STATUS_ERROR, message="获取用户信息失败")
