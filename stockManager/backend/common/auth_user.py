"""认证用户类型收窄（django-stubs 下 request.user 为 _AnyUser）。"""
from typing import cast

from django.contrib.auth.models import User
from django.http import HttpRequest


def authenticated_user(request: HttpRequest) -> User:
    """在 @require_authentication 之后将 request.user 收窄为具体 User。"""
    return cast(User, request.user)
