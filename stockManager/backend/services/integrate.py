from decimal import Decimal
from typing import Dict, ClassVar, Tuple, Optional

from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .calculator import Caculator
from ..models import Operation, Info, CashFlow
from ..utils import format_operations
from ..common import logger


class Integrate:
    """
    集成类，用于管理和缓存 Caculator 实例
    """

    # 类变量：用户 ID 到 Caculator 实例的映射
    caculator_map: ClassVar[Dict[int, Caculator]] = {}

    @classmethod
    def _get_user_cash_info(cls, user) -> Tuple[float, float]:
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
        获取或创建 Caculator 实例（带缓存机制）
        
        Args:
            user: User 对象
            
        Returns:
            Caculator 实例
        """
        user_id = user.id
        cached_caculator = cls.caculator_map.get(user_id)
        
        # 如果缓存存在，直接返回（数据变化时会通过信号自动清除缓存）
        if cached_caculator is not None:
            logger.debug(f"缓存命中 - 用户 ID: {user_id}, 用户名: {user.username}")
            return cached_caculator
        
        # 缓存不存在，需要创建
        logger.debug(f"缓存未命中 - 用户 ID: {user_id}, 用户名: {user.username}, 开始创建 Caculator 实例")
        
        # 获取操作记录并格式化
        operations = Operation.objects.filter(user=user).order_by("date")
        operation_list = format_operations(operations)
        
        # 获取用户的资金信息
        origin_cash, income_cash = cls._get_user_cash_info(user)
        
        # 创建新实例
        new_caculator = Caculator(
            operation_list, 
            user,
            origin_cash,
            income_cash
        )
        cls.caculator_map[user_id] = new_caculator
        return new_caculator

    @classmethod
    def clear_cache(cls, user_id: Optional[int] = None):
        """
        清除缓存
        
        Args:
            user_id: 用户 ID，如果为 None 则清除所有缓存
        """
        if user_id is None:
            cls.caculator_map.clear()
        else:
            cls.caculator_map.pop(user_id, None)


# 信号监听器：监听模型变化，自动清除缓存

def clear_integrate_cache(sender, instance, **kwargs):
    """
    监听 Operation、CashFlow、Info 模型保存和删除信号，自动清除对应用户的缓存
    
    Args:
        sender: 发送信号的模型类
        instance: 模型实例
        **kwargs: 其他参数
    """
    # Info 模型只有 INCOME_CASH 类型才需要清除缓存
    if sender == Info:
        if not (instance.user_id and instance.info_type == Info.InfoType.INCOME_CASH):
            return
    
    # Operation 和 CashFlow 直接清除缓存
    if instance.user_id:
        Integrate.clear_cache(instance.user_id)


# 为三个模型注册信号监听器
for signal in [post_save, post_delete]:
    for model in [Operation, CashFlow, Info]:
        signal.connect(clear_integrate_cache, sender=model)
