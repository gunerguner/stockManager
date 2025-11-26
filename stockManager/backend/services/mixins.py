"""Mixin 模块"""
from typing import Dict, List
from .calculator import Calculator
from .dividend import Dividend


class CalculatorMixin:
    """计算指标能力"""
    def calculate_target(self) -> Dict:
        return Calculator.calculate_target(self.operation_list, self.origin_cash, self.income_cash)


class DividendMixin:
    """分红能力"""
    def generate_dividend(self) -> List[str]:
        return Dividend.generate_dividend(self.user, self.operation_list)

