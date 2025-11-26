"""
常量定义模块
"""
from enum import IntEnum, Enum


class ResponseStatus(IntEnum):
    """响应状态码枚举"""
    SUCCESS = 1  # 操作成功
    ERROR = 0  # 操作失败
    UNAUTHORIZED = 302  # 未登录/未授权


class OperationType(str, Enum):
    """操作类型枚举"""
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DV"

