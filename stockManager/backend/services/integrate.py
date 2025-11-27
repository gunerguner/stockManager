from decimal import Decimal
from typing import Dict, ClassVar, Tuple, Optional, List, Any
from django.contrib.auth.models import User

from django.db.models import Sum
from django.db.models.signals import post_save, post_delete

from .userData import UserData
from ..models import Operation, Info, CashFlow
from ..utils import format_operations
from ..common import logger


class Integrate:
    """
    集成类，用于管理和缓存 UserData 实例
    """

    # 类变量：用户 ID 到 UserData 实例的映射
    user_data_map: ClassVar[Dict[int, UserData]] = {}

    @classmethod
    def _get_operation_list(cls, user: User) -> Dict[str, List[Operation]]:
        """获取用户的操作记录字典"""
        return format_operations(Operation.objects.filter(user=user).order_by("date"))
    
    @classmethod
    def _get_user_cash_info(cls, user: User) -> Tuple[float, float]:
        """获取用户的资金信息"""
        origin_cash = float(CashFlow.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))
        income_cash_info = Info.objects.filter(user=user, info_type=Info.InfoType.INCOME_CASH).first()
        income_cash = float(income_cash_info.value) if income_cash_info else 0.0
        return origin_cash, income_cash


    @classmethod
    def get_user_data(cls, user: User) -> UserData:
        """获取或创建 UserData 实例（带缓存机制）"""
        if user.id in cls.user_data_map:
            logger.debug(f"缓存命中: 用户 {user.id} ({user.username}) 的 UserData 从缓存中获取")
            return cls.user_data_map[user.id]
        
        logger.debug(f"缓存未命中: 为用户 {user.id} ({user.username}) 创建新的 UserData 实例")
        origin_cash, income_cash = cls._get_user_cash_info(user)
        user_data = UserData(user, cls._get_operation_list(user), income_cash, origin_cash)
        cls.user_data_map[user.id] = user_data
        return user_data
    
    @classmethod
    def calculate_target(cls, user: User) -> Dict[str, Any]:
        """计算股票指标"""
        return cls.get_user_data(user).calculate_target()
    
    @classmethod
    def generate_dividend(cls, user: User) -> List[str]:
        """为持有的股票生成分红数据"""
        return cls.get_user_data(user).generate_dividend()

    @classmethod
    def clear_cache(cls, user_id: Optional[int] = None):
        """清除缓存"""
        cls.user_data_map.clear() if user_id is None else cls.user_data_map.pop(user_id, None)


# 信号监听器：监听模型变化，自动清除缓存

def clear_integrate_cache(sender: Any, instance: Any, **kwargs: Any):
    """监听模型变化，自动清除对应用户的缓存"""
    if sender == Info and not (instance.user_id and instance.info_type == Info.InfoType.INCOME_CASH):
        return
    if instance.user_id:
        Integrate.clear_cache(instance.user_id)


# 为三个模型注册信号监听器
for signal in [post_save, post_delete]:
    for model in [Operation, CashFlow, Info]:
        signal.connect(clear_integrate_cache, sender=model)
