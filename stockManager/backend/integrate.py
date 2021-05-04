from .caculator import Caculator
from .models import Operation, Info
from .utils import format_operations, query_realtime_price


class Integrate(object):

    caculator_map = {}

    @classmethod
    def caculator(cls, username, realtime):
        operations = Operation.objects.all().order_by("date")  # 获取所有操作记录
        new_operation_list = format_operations(operations)  # 操作记录格式化

        

        to_return = cls.caculator_map.get(username)

        if to_return is not None and realtime == False:
            to_return.operation_list = new_operation_list
            return to_return

        realtime_price_list = query_realtime_price(
            list(new_operation_list.keys())
        )  # 持仓股票的现价

        if to_return is None:
            to_return = Caculator(new_operation_list, realtime_price_list)
            cls.caculator_map[username] = to_return
        else:
            to_return.operation_list = new_operation_list
            to_return.realtime_list = realtime_price_list

        return to_return