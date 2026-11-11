"""
常量定义模块
"""
from enum import IntEnum

from django.db import models
from django.utils.translation import gettext_lazy as _


class ResponseStatus(IntEnum):
    """响应状态码枚举"""
    SUCCESS = 1  # 操作成功
    ERROR = 0  # 操作失败
    UNAUTHORIZED = 401  # 未登录/未认证


class OperationType(models.TextChoices):
    """操作类型枚举"""
    BUY = "BUY", _("买入")
    SELL = "SELL", _("卖出")
    DIVIDEND = "DV", _("除权除息")
