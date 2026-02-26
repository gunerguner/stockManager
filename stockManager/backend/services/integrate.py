"""
用户数据集成模块，使用 Redis 缓存优化性能

集成服务(外观模式)，提供统一的业务入口，协调各个领域服务完成业务逻辑。
"""
from typing import List, Any
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete

from .cacheRepository import CacheRepository
from .calculator import Calculator
from .dividend import Dividend
from ..models import Operation, Info, CashFlow
from ..common import logger
from ..common.types import CalculatedResult, OperationDataDict


class Integrate:
    """
    集成服务类(外观模式)
    
    提供统一的业务入口，协调用户数据获取、股票计算、分红生成等功能。
    负责缓存管理和数据协调，不包含具体业务逻辑。
    """
    @classmethod
    def get_operations(cls, user: User) -> OperationDataDict:
        """获取用户的操作列表（序列化为字典格式）"""
        operation_list = CacheRepository.get_user_operations(user)
        return {
            code: [op.to_dict() for op in reversed(ops)]
            for code, ops in operation_list.items()
        }
    
    @classmethod
    def get_calculated_result(cls, user: User) -> CalculatedResult:
        """获取计算结果（不含 operationList）"""
        cached_result = CacheRepository.get_calculated_target(user)
        if cached_result is not None:
            return cached_result
        
        operation_list = CacheRepository.get_user_operations(user)
        stock_list = Calculator.calculate_stock_list(operation_list)
        
        income_cash, cash_flow_list = CacheRepository.get_user_cash_info(user)
        overall = Calculator.calculate_overall(stock_list, income_cash, cash_flow_list)
        
        result: CalculatedResult = {"stocks": stock_list, "overall": overall}
        CacheRepository.set_calculated_target(user.id, result)
        
        return result
    
    @classmethod
    def generate_dividend(cls, user: User) -> List[str]:
        """生成股票分红数据"""
        operation_list = CacheRepository.get_user_operations(user)
        # 直接调用分红服务
        return Dividend.generate_dividend(user, operation_list)
    
    @classmethod
    def update_income_cash(cls, user: User, income_cash: float) -> None:
        """更新收益现金（逆回购等收入）"""
        Info.objects.update_or_create(
            user=user,
            info_type=Info.InfoType.INCOME_CASH,
            defaults={'value': str(income_cash)}
        )
        # 清除缓存，确保下次获取时使用最新数据

        if user.id is None:
            logger.warning("不支持清除所有用户缓存")
            return
        CacheRepository.clear_user_cache(user.id)
        logger.info(f"用户 {user.username} 更新收益现金: {income_cash}")

def clear_integrate_cache(sender: Any, instance: Any, **kwargs: Any):
    """信号处理：模型变化时清除相关 Redis 缓存"""
    # Info 模型只处理 INCOME_CASH 类型
    if sender == Info and not (instance.user_id and instance.info_type == Info.InfoType.INCOME_CASH):
        return
    
    if instance.user_id:
        model_name = sender.__name__
        CacheRepository.clear_user_cache(instance.user_id)
        logger.info(f"[Redis] {model_name} 变化，清除用户 {instance.user_id} 的缓存")

# 注册信号监听器：Operation、CashFlow、Info 变化时自动清除缓存
for signal in [post_save, post_delete]:
    for model in [Operation, CashFlow, Info]:
        signal.connect(clear_integrate_cache, sender=model)
