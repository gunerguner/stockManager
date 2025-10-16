from .caculator import Caculator
from .models import Operation, StockMeta
from .utils import format_operations, query_realtime_price


class Integrate:
    """
    集成类，用于管理和缓存 Caculator 实例
    """

    caculator_map = {}

    @classmethod
    def caculator(cls, username, realtime):
        """
        获取或创建 Caculator 实例
        
        Args:
            username: 用户名
            realtime: 是否获取实时价格
            
        Returns:
            Caculator 实例
        """
        # 获取所有操作记录并格式化
        operations = Operation.objects.all().order_by("date")
        new_operation_list = format_operations(operations)

        # 获取缓存的 Caculator 实例
        cached_caculator = cls.caculator_map.get(username)

        # 如果不需要实时价格且缓存存在，直接返回缓存
        if cached_caculator is not None and not realtime:
            cached_caculator.operation_list = new_operation_list
            return cached_caculator

        # 查询实时价格
        realtime_price_list = query_realtime_price(list(new_operation_list.keys()))

        # 创建或更新 Caculator 实例
        if cached_caculator is None:
            # 创建新实例
            new_caculator = Caculator(new_operation_list, realtime_price_list)
            cls.caculator_map[username] = new_caculator
            return new_caculator
        else:
            # 更新已有实例
            cached_caculator.operation_list = new_operation_list
            cached_caculator.realtime_list = realtime_price_list
            cached_caculator.stockMeta = StockMeta.objects.all()
            return cached_caculator
