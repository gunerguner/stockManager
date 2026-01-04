"""用户数据集成模块，使用 Redis 缓存优化性能"""
from datetime import datetime
from typing import Dict, Optional, List, Any
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete

from .userData import UserData
from .cacheManager import CacheManager
from ..models import Operation, Info, CashFlow
from ..utils import format_operations
from ..common import logger
from ..common.tradingCalendar import TradingCalendar, TZ_SHANGHAI


class Integrate:
    """集成类，提供用户数据查询和缓存管理"""

    @classmethod
    def _get_operation_list(cls, user: User) -> Dict[str, List[Operation]]:
        """获取用户操作记录（支持 Redis 缓存）"""
        # 先查 Redis，未命中则查数据库并缓存
        cached = CacheManager.get_user_operations(user)
        if cached is not None:
            return cached
        
        operations = format_operations(Operation.objects.filter(user=user).order_by("date"))
        CacheManager.set_user_operations(user, operations)
        return operations
    
    @classmethod
    def _get_user_cash_info(cls, user: User) -> tuple[float, List[Dict[str, Any]]]:
        """获取用户资金信息（支持 Redis 缓存）"""
        # 先查 Redis，未命中则查数据库并缓存
        cached = CacheManager.get_user_cash_info(user)
        if cached is not None:
            return cached
        
        # 查询现金收入
        income_info = Info.objects.filter(user=user, info_type=Info.InfoType.INCOME_CASH).first()
        income_cash = float(income_info.value) if income_info else 0.0
        
        # 查询出入金记录
        cash_flows = CashFlow.objects.filter(user=user).order_by('-transaction_date')
        cash_flow_list = [
            {'date': str(flow.transaction_date), 'amount': float(flow.amount)}
            for flow in cash_flows
        ]
        
        CacheManager.set_user_cash_info(user, income_cash, cash_flow_list)
        return income_cash, cash_flow_list

    @classmethod
    def get_user_data(cls, user: User) -> UserData:
        """获取用户数据实例"""
        income_cash, cash_flow_list = cls._get_user_cash_info(user)
        operation_list = cls._get_operation_list(user)
        return UserData(user, operation_list, income_cash, cash_flow_list)
    
    @classmethod
    def calculate_target(cls, user: User) -> Dict[str, Any]:
        """计算股票指标（支持结果缓存）"""
        # 尝试从缓存获取
        cached_result = CacheManager.get_calculated_target(user.id)
        if cached_result is not None:
            return cached_result
        
        # 缓存未命中，执行计算
        user_data = cls.get_user_data(user)
        result = user_data.calculate_target()
        
        # 写入缓存（根据交易时间决定 TTL）
        current_time = datetime.now(TZ_SHANGHAI)
        ttl = (
            CacheManager.TTL_CALCULATED_TARGET_TRADING 
            if TradingCalendar.is_in_trading_hours(current_time) 
            else CacheManager.TTL_CALCULATED_TARGET_NON_TRADING
        )
        CacheManager.set_calculated_target(user.id, result, ttl)
        
        return result
    
    @classmethod
    def generate_dividend(cls, user: User) -> List[str]:
        """生成股票分红数据"""
        user_data = cls.get_user_data(user)
        return user_data.generate_dividend()

    @classmethod
    def clear_cache(cls, user_id: Optional[int] = None):
        """清除用户缓存"""
        if user_id is None:
            logger.warning("不支持清除所有用户缓存")
            return
        CacheManager.clear_user_operations(user_id)
        CacheManager.clear_user_cash_info(user_id)
        CacheManager.clear_calculated_target(user_id)  # 清除计算结果缓存


def clear_integrate_cache(sender: Any, instance: Any, **kwargs: Any):
    """信号处理：模型变化时清除相关 Redis 缓存"""
    # Info 模型只处理 INCOME_CASH 类型
    if sender == Info and not (instance.user_id and instance.info_type == Info.InfoType.INCOME_CASH):
        return
    
    if instance.user_id:
        model_name = sender.__name__
        CacheManager.clear_user_operations(instance.user_id)
        CacheManager.clear_user_cash_info(instance.user_id)
        CacheManager.clear_calculated_target(instance.user_id)  # 清除计算结果缓存
        logger.info(f"[Redis] {model_name} 变化，清除用户 {instance.user_id} 的缓存")


# 注册信号监听器：Operation、CashFlow、Info 变化时自动清除缓存
for signal in [post_save, post_delete]:
    for model in [Operation, CashFlow, Info]:
        signal.connect(clear_integrate_cache, sender=model)
