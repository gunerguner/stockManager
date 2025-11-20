"""
Admin 基础配置模块
提供公共的导入和配置
"""
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth import get_user_model

from ..models import Operation, Info, StockMeta, CashFlow

# 获取 User 模型，供所有 admin 模块使用
User = get_user_model()

__all__ = ['admin', 'messages', 'User', 'Operation', 'Info', 'StockMeta', 'CashFlow']

