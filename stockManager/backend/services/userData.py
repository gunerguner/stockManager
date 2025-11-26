"""用户数据模块"""
from typing import Dict
from django.contrib.auth.models import User
from .mixins import CalculatorMixin, DividendMixin


class UserData(CalculatorMixin, DividendMixin):
    """用户数据类，管理用户维度的数据"""
    
    def __init__(self, user: User, operation_list: Dict[str, list], income_cash: float, origin_cash: float):
        self.user = user
        self.operation_list = operation_list
        self.income_cash = income_cash
        self.origin_cash = origin_cash

