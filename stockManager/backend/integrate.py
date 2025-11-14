from .caculator import Caculator
from .models import Operation, Info
from .utils import format_operations, query_realtime_price


class Integrate:
    """
    集成类，用于管理和缓存 Caculator 实例
    """

    caculator_map = {}

    @classmethod
    def caculator(cls, user, realtime):
        """
        获取或创建 Caculator 实例
        
        Args:
            user: User 对象
            realtime: 是否获取实时价格
            
        Returns:
            Caculator 实例
        """
        # 获取该用户的操作记录并格式化
        operations = Operation.objects.filter(user=user).order_by("date")
        new_operation_list = format_operations(operations)

        # 获取用户的资金信息（每次查询数据库）
        origin_cash_info = Info.objects.filter(
            user=user,
            info_type=Info.InfoType.ORIGIN_CASH
        ).first()
        income_cash_info = Info.objects.filter(
            user=user,
            info_type=Info.InfoType.INCOME_CASH
        ).first()
        
        origin_cash = float(origin_cash_info.value) if origin_cash_info else 0.0
        income_cash = float(income_cash_info.value) if income_cash_info else 0.0

        # 使用用户 ID 作为缓存 key
        user_id = user.id
        cached_caculator = cls.caculator_map.get(user_id)

        # 如果不需要实时价格且缓存存在，直接返回缓存
        if cached_caculator is not None and not realtime:
            cached_caculator.operation_list = new_operation_list
            cached_caculator.origin_cash = origin_cash
            cached_caculator.income_cash = income_cash
            return cached_caculator

        # 查询实时价格
        realtime_price_list = query_realtime_price(list(new_operation_list.keys()))

        # 创建或更新 Caculator 实例
        if cached_caculator is None:
            # 创建新实例
            new_caculator = Caculator(
                new_operation_list, 
                realtime_price_list, 
                user,
                origin_cash,
                income_cash
            )
            cls.caculator_map[user_id] = new_caculator
            return new_caculator
        else:
            # 更新已有实例
            cached_caculator.operation_list = new_operation_list
            cached_caculator.realtime_list = realtime_price_list
            cached_caculator.user = user  # 确保 user 是最新的
            cached_caculator.origin_cash = origin_cash
            cached_caculator.income_cash = income_cash
            # StockMeta 使用全局缓存，自动共享，无需更新
            return cached_caculator
