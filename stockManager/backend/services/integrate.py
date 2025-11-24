from decimal import Decimal
from typing import Dict, ClassVar

from django.db.models import Sum

from .calculator import Caculator
from ..models import Operation, Info, CashFlow
from ..utils import format_operations


class Integrate:
    """
    集成类，用于管理和缓存 Caculator 实例
    """

    # 类变量：用户 ID 到 Caculator 实例的映射
    caculator_map: ClassVar[Dict[int, Caculator]] = {}

    @classmethod
    def _get_user_cash_info(cls, user):
        """
        获取用户的资金信息
        
        Args:
            user: User 对象
            
        Returns:
            tuple: (origin_cash, income_cash) 本金和收益现金
        """
        # 从 CashFlow 表计算本金（所有金额的累计）
        total_amount = CashFlow.objects.filter(user=user).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        origin_cash = float(total_amount)
        
        # 从 Info 表获取收益现金（保持不变）
        income_cash_info = Info.objects.filter(
            user=user,
            info_type=Info.InfoType.INCOME_CASH
        ).first()
        income_cash = float(income_cash_info.value) if income_cash_info else 0.0
        
        return origin_cash, income_cash

    @classmethod
    def caculator(cls, user):
        """
        获取或创建 Caculator 实例
        
        Args:
            user: User 对象
            
        Returns:
            Caculator 实例
        """
        # 获取该用户的操作记录并格式化
        operations = Operation.objects.filter(user=user).order_by("date")
        new_operation_list = format_operations(operations)

        # 获取用户的资金信息（每次查询数据库）
        origin_cash, income_cash = cls._get_user_cash_info(user)

        # 使用用户 ID 作为缓存 key
        user_id = user.id
        cached_caculator = cls.caculator_map.get(user_id)

        # 创建或更新 Caculator 实例（实时价格在需要时动态获取）
        if cached_caculator is None:
            # 创建新实例
            new_caculator = Caculator(
                new_operation_list, 
                user,
                origin_cash,
                income_cash
            )
            cls.caculator_map[user_id] = new_caculator
            return new_caculator
        else:
            # 更新已有实例
            cached_caculator.operation_list = new_operation_list
            cached_caculator.user = user  # 确保 user 是最新的
            cached_caculator.origin_cash = origin_cash
            cached_caculator.income_cash = income_cash
            return cached_caculator
