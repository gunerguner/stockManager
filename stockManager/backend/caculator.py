import datetime
import baostock as bs
from .models import Operation, Info, StockMeta


class Caculator(object):
    def __init__(self, operation_list, realtime_list):
        self.operation_list = operation_list  # 交易列表
        self.realtime_list = realtime_list  # 实时价格

        self.stockMeta = StockMeta.objects.all()

    # 聚合接口，所有的股票数据+总和
    def caculate_target(self):
        to_return = {}
        stock_list = []

        # 个股指标
        for key in self.operation_list.keys():
            single_target = self.__caculate_single_target(key)
            stock_list.append(single_target)

        to_return["stocks"] = stock_list

        # 整体指标
        to_return["overall"] = self.__caculate_overall_target(stock_list)

        return to_return

    def generate_divident(self):

        hold_stocks = self.all_stocks(True)

        to_return = []
        bs.login()
        for single_code in hold_stocks:
            name = self.__generate_divident_single(single_code)
            if len(name) > 0:
                to_return.append(name)

        bs.logout()

        return to_return

    # 现有持仓
    def all_stocks(self, hold=False):

        overall_stocks = list(self.operation_list.keys())
        if hold == False:
            return overall_stocks

        hold_stocks = list(
            filter(
                lambda x: self.__caculate_single_holdCount(self.operation_list[x]) > 0,
                overall_stocks,
            )
        )

        return hold_stocks

    # 生成个股除权除息
    def __generate_divident_single(self, code):
        if code is None:
            return ""

        to_return = 0
        single_operation_list = self.operation_list[code]
        single_real_time = self.realtime_list[code]
        name = single_real_time[0]

        exist_dv_operations = list(
            filter(lambda x: x.operationType == "DV", single_operation_list)
        )
        date_array = list(map(lambda x: str(x.date), exist_dv_operations))

        first_year = single_operation_list[0].date.year

        year_now = datetime.date.today().year
        new_code = code[0:2] + "." + code[2:]

        for year in range(int(first_year), int(year_now) + 1, 1):
            rs = bs.query_dividend_data(
                code=new_code, year=str(year), yearType="operate"
            )
            while (rs.error_code == "0") & rs.next():
                data = rs.get_row_data()
                date = data[6]
                cash = 0 if data[9] == "" else float(data[9])
                reserve = 0 if data[11] == "" else float(data[11])
                stock = 0 if data[13] == "" else float(data[13])

                find = False
                for exist_date in date_array:
                    if exist_date == date:
                        find = True

                if find == False:
                    Operation.objects.create(
                        date=date,
                        code=code,
                        operationType="DV",
                        cash=cash,
                        reserve=reserve,
                        stock=stock,
                    )
                    to_return += 1

        operations = Operation.objects.filter(code=code).order_by("date")
        current_hold = 0
        for operation in operations:
            if operation.operationType == "BUY":
                current_hold += operation.count
            elif operation.operationType == "SELL":
                current_hold -= operation.count
            elif operation.operationType == "DV":
                if current_hold == 0:
                    operation.delete()
                    to_return -= 1
                else:
                    operation.count = current_hold
                    operation.save()
                    current_hold += current_hold * (operation.reserve + operation.stock)

        if to_return > 0:
            return name
        else:
            return ""

    # 计算个股指标
    def __caculate_single_target(self, key):
        if key is None:
            return ""
        to_return = {}

        # 带上股票的标签
        stockType = list(filter(lambda x: x.code == key, self.stockMeta))
        if len(stockType) > 0:
            to_return["stockType"] = stockType[0].stockType
            to_return["isNew"] = stockType[0].isNew

        single_operation_list = self.operation_list[key]
        single_real_time = self.realtime_list[key]

        to_return["code"] = key
        to_return["name"] = single_real_time[0]  # 名称
        to_return["priceNow"] = single_real_time[1]  # 现价
        if float(to_return["priceNow"]) < 0.001:
            to_return["offsetToday"] = 0  # 今日股价涨跌
            to_return["offsetTodayRatio"] = "0%"  # 今日涨跌率
        else:
            to_return["offsetToday"] = single_real_time[2]  # 今日股价涨跌
            to_return["offsetTodayRatio"] = single_real_time[3]  # 今日涨跌率

        current_hold_count = self.__caculate_single_holdCount(single_operation_list)
        to_return["holdCount"] = current_hold_count  # 持股数
        current_hold_cost = self.__caculate_single_hold_cost(single_operation_list)
        to_return["holdCost"] = current_hold_cost  # 持仓成本
        current_overall = self.__caculate_single_overall(single_operation_list)
        to_return["overallCost"] = (
            current_overall / current_hold_count if current_hold_cost > 0 else 0
        )  # 摊薄成本
        to_return["totalValue"] = (
            float(single_real_time[1]) * current_hold_count
        )  # 今日市值
        yesterday_hold_count = self.__caculate_single_holdCount(
            single_operation_list, 1
        )
        to_return["totalValueYesterday"] = (
            float(single_real_time[4]) * yesterday_hold_count
        )  # 昨日市值，不显示

        current_offset = (
            float(single_real_time[1]) - current_hold_cost
        ) * current_hold_count
        to_return["offsetCurrent"] = current_offset  # 浮动盈亏额
        current_offset_ratio = (
            (float(single_real_time[1]) - current_hold_cost) / current_hold_cost
            if current_hold_cost > 0
            else 0
        )
        to_return["offsetCurrentRatio"] = "%.2f%%" % (
            current_offset_ratio * 100
        )  # 浮动盈亏率

        to_return["offsetTotal"] = (
            float(single_real_time[1]) * current_hold_count - current_overall
        )  # 累计盈亏额

        to_return["totalCost"] = self.__caculate_single_fee(single_operation_list)
        # 所有费用

        to_return["operationList"] = self.__caculate_single_operation_list(
            single_operation_list
        )

       

        total_offset_today = 0
        if to_return["totalValueYesterday"] < 0.1:
            total_offset_today = current_offset  # 今天新买的，今日盈亏等于浮动盈亏
        else:
            total_offset_today = (
                float(single_real_time[1]) * current_hold_count
                - float(single_real_time[4]) * yesterday_hold_count
                - self.__caculate_single_today_input(single_operation_list)
            )

        to_return["totalOffsetToday"] = total_offset_today  # 今日盈亏，不显示

        return to_return

    def __caculate_single_operation_list(self, single_operation_list):
        to_return = []
        for single_operation in single_operation_list:
            to_return.append(single_operation.to_dict())

        to_return.reverse()
        return to_return

    def __caculate_single_holdCount(self, single_operation_list, yesterday=0):
        # 某个股票当前持股数，这里假设已经按照时间排好序了，算是个小坑
        current_hold = 0
        for single_operation in single_operation_list:
            today = datetime.date.today()
            if yesterday == 1:
                # 只计算到昨天的持仓
                if single_operation.date >= today:
                    continue

            if single_operation.operationType == "BUY":
                current_hold += single_operation.count
            elif single_operation.operationType == "SELL":
                current_hold -= single_operation.count
            elif single_operation.operationType == "DV":
                current_hold += current_hold * (
                    single_operation.reserve + single_operation.stock
                )

        return current_hold

    def __caculate_single_hold_cost(self, single_operation_list):
        # 某个股票的持仓成本
        total_pay = 0
        current_hold = 0
        total_count = 0
        for single_operation in single_operation_list:
            if single_operation.operationType == "BUY":
                current_hold += single_operation.count
                total_pay += (
                    single_operation.count * single_operation.price
                    + single_operation.fee
                )
                total_count += single_operation.count
            elif single_operation.operationType == "SELL":
                current_hold -= single_operation.count
            elif single_operation.operationType == "DV":
                total_count += total_count * (
                    single_operation.reserve + single_operation.stock
                )
                current_hold += current_hold * (
                    single_operation.reserve + single_operation.stock
                )

            if current_hold == 0:
                # 这里有个大坑，如果清仓了就不算，重头算起
                total_pay = 0
                total_count = 0

        return total_pay / total_count if total_count > 0 else 0

    def __caculate_single_overall(self, single_operation_list):
        # 某个股票的摊薄成本
        current_hold = 0
        current_sum = 0
        for single_operation in single_operation_list:
            if single_operation.operationType == "BUY":
                current_hold += single_operation.count
                current_sum += (
                    single_operation.count * single_operation.price
                    + single_operation.fee
                )
            elif single_operation.operationType == "SELL":
                current_hold -= single_operation.count
                current_sum -= (
                    single_operation.count * single_operation.price
                    - single_operation.fee
                )
            elif single_operation.operationType == "DV":
                current_sum -= current_hold * single_operation.cash
                current_hold += current_hold * (
                    single_operation.reserve + single_operation.stock
                )

        return current_sum

    def __caculate_single_today_input(self, single_operation_list):
        # 某个股票今天的净投入
        today_operation = 0
        for single_operation in single_operation_list:
            today = datetime.date.today()
            # 只计算今天的持仓
            if single_operation.date != today:
                continue
            if single_operation.operationType == "BUY":
                today_operation += (
                    single_operation.count * single_operation.price
                    + single_operation.fee
                )
            elif single_operation.operationType == "SELL":
                today_operation -= (
                    single_operation.count * single_operation.price
                    + single_operation.fee
                )

        return today_operation

    def __caculate_single_fee(self, single_target_list):
        current_sum = 0
        for single_operation in single_target_list:
            current_sum += single_operation.fee

        return current_sum

    def __caculate_overall_target(self, single_target_list):
        to_return = {}
        current_offset = 0
        total_offset = 0
        total_value = 0
        total_offset_today = 0
        total_cost = 0

        origin_cash = float(Info.objects.get(key="originCash").value)
        income_cash = float(Info.objects.get(key="incomeCash").value)

        for single_target in single_target_list:
            current_offset += single_target["offsetCurrent"]
            total_offset += single_target["offsetTotal"]
            total_value += single_target["totalValue"]
            total_offset_today += single_target["totalOffsetToday"]
            total_cost += single_target["totalCost"]

        to_return["offsetCurrent"] = current_offset  # 浮动盈亏
        to_return["offsetTotal"] = total_offset + income_cash  # 累计盈亏
        to_return["totalValue"] = total_value  # 总市值
        to_return["offsetCurrentRatio"] = "%.2f%%" % (
            (current_offset / total_value * 100) if total_value > 0 else 0
        )  # 浮动盈亏率
        to_return["offsetToday"] = total_offset_today  # 今日盈亏

        to_return["totalCash"] = (
            origin_cash + total_offset + income_cash - total_value
        )  # 总现金
        to_return["totalAsset"] = origin_cash + total_offset + income_cash  # 总资产
        to_return["totalCost"] = total_cost  # 总费用

        to_return["incomeCash"] = income_cash  # 逆回购等收入
        to_return["originCash"] = origin_cash  # 本金

        return to_return


"""
计算公式：

1、成本价
持股数 = ∑买入数量 + ∑红股数量 + ∑拆股所增数量 - ∑卖出数量 - ∑合股所减数量
摊薄成本 = (∑买入金额 - ∑卖出金额 - ∑现金股息) / 持股数
持仓成本 = ∑买入金额 / (∑买入数量 + ∑红股数量 + ∑拆股所增数量 - ∑合股所减数量) 
2、浮动盈亏
浮动盈亏额 ＝ (当前价 - 持仓成本) * 多仓持股数
浮动盈亏率 ＝ 浮动盈亏额 / (持仓成本价 * 持股数)
分市场浮动盈亏额 ＝ ∑个股浮动盈亏额
分市场浮动盈亏率 ＝ 分市场浮动盈亏额 / ∑(个股持仓成本 * 个股持股数)
3、累计盈亏
个股累计盈亏额 ＝ 多仓市值 - (∑买入金额 - ∑卖出金额 - ∑现金股息) 
个股累计盈亏率 ＝ 累计盈亏额 / ∑买入金额
分市场累计盈亏额 ＝ ∑个股累计盈亏额
无银转
分市场累计盈亏率 ＝ 累计盈亏额 / ∑个股买入金额
有银转
分市场累计盈亏率 = 累计盈亏额 / ∑转入金额
4、当日盈亏
昨日市值 > 0
当日盈亏额 = (现市值 - 昨收市值 + 当日∑卖出 - 当日∑买入)
当日盈亏率 = 当日盈亏额 / (昨市值 + 当日∑买入 + 当日∑卖空)
昨日市值 = 0
当日盈亏额 = (现价 - 持仓成本) * 股数
当日盈亏率 = 当日盈亏额 / 当日∑买入

现金 = 本金+累计盈亏-市值

每个股票对应的指标
code, name，priceNow，offsetToday，offsetTodayRatio，totalValue，holdCount，holdCost，overallCost，offsetCurrent，offsetCurrentRatio，offsetTotal

整体指标
offsetToday，offsetCurrent，offsetCurrentRatio，offsetTotal，totalValue，totalCash，originCash
"""
