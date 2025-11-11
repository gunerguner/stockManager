"""
股票计算器模块
提供股票指标计算、分红处理等功能
"""
import datetime
from typing import Dict, List, Optional

import baostock as bs

from .common import logger
from .models import Operation, Info, StockMeta
from .utils import _safe_float

# 常量定义
OPERATION_TYPE_BUY = "BUY"
OPERATION_TYPE_SELL = "SELL"
OPERATION_TYPE_DIVIDEND = "DV"
INFO_KEY_ORIGIN_CASH = "originCash"
INFO_KEY_INCOME_CASH = "incomeCash"
DIVIDEND_DATE_CHECK_RANGE = 5  # 分红日期检查范围（前后天数）


class Caculator(object):
    """股票计算器类，用于计算股票相关指标"""
    
    def __init__(self, operation_list: Dict, realtime_list: Dict):
        """
        初始化计算器
        
        Args:
            operation_list: 交易操作列表字典
            realtime_list: 实时价格字典
        """
        self.operation_list = operation_list
        self.realtime_list = realtime_list
        self.stockMeta_dict = {meta.code: meta for meta in StockMeta.objects.all()}
    
    @property
    def _today(self) -> datetime.date:
        """
        获取今天的日期（使用property确保跨天时获取正确日期）
        注意：在需要多次使用的方法中，建议将其赋值给局部变量以提升性能
        """
        return datetime.date.today()

    # 聚合接口,所有的股票数据+总和
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

    def generate_dividend(self):

        hold_stocks = self.all_stocks(True)

        to_return = []
        bs.login()
        for single_code in hold_stocks:
            name = self.__generate_dividend_single(single_code)
            if len(name) > 0:
                to_return.append(name)

        bs.logout()

        return to_return

    # 现有持仓
    def all_stocks(self, hold=False):
        """获取所有股票代码，如果 hold=True 则只返回持仓股票"""
        overall_stocks = list(self.operation_list.keys())
        if not hold:
            return overall_stocks

        hold_stocks = [
            stock
            for stock in overall_stocks
            if self.__caculate_single_holdCount(self.operation_list[stock]) > 0
        ]

        return hold_stocks

    def __is_date_near_existing(self, date_str: str, existing_dates: set, today: datetime.date) -> bool:
        """
        检查日期是否在已有日期列表中,或在已有日期的前后指定天数范围内
        
        Args:
            date_str: 要检查的日期字符串 (格式: YYYY-MM-DD)
            existing_dates: 已存在的日期集合
            today: 今天的日期对象，避免重复调用
            
        Returns:
            bool: True 表示日期已存在或接近已有日期或是未来日期, False 表示是新日期
        """
        if date_str in existing_dates:
            return True
        
        try:
            # 将字符串转换为日期对象
            current_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # 检查除权除息日是否晚于今天(未来日期不允许)
            if current_date > today:
                return True
            
            # 检查前后指定天数范围
            for days_offset in range(1, DIVIDEND_DATE_CHECK_RANGE + 1):
                one_day = datetime.timedelta(days=days_offset)
                previous_day = (current_date - one_day).strftime('%Y-%m-%d')
                next_day = (current_date + one_day).strftime('%Y-%m-%d')
                
                # 如果前后任意一天在已有日期中,认为是重复的
                if previous_day in existing_dates or next_day in existing_dates:
                    return True
                
            return False
            
        except (ValueError, TypeError) as e:
            logger.warning(f"日期格式解析失败: {date_str}, 错误: {e}")
            # 如果日期格式有问题,只检查是否完全相同
            return date_str in existing_dates


    def __generate_dividend_single(self, code: Optional[str]) -> str:
        """
        生成个股除权除息信息
        
        Args:
            code: 股票代码
            
        Returns:
            str: 如果有更新返回股票名称，否则返回空字符串
        """
        if code is None:
            return ""

        try:
            # 在方法开始时获取today并赋值给局部变量，避免重复调用property
            today = self._today
            update_count = 0
            single_operation_list = self.operation_list[code]
            single_real_time = self.realtime_list[code]
            name = single_real_time[0]

            # 获取已存在的分红操作记录
            exist_dv_operations = [
                op for op in single_operation_list 
                if op.operationType == OPERATION_TYPE_DIVIDEND
            ]
            # 将日期列表转换为集合,提升查找效率(O(1) vs O(n))
            date_set = {str(op.date) for op in exist_dv_operations}

            first_year = single_operation_list[0].date.year
            year_now = today.year
            # 转换股票代码格式: sz000001 -> sz.000001
            formatted_code = f"{code[:2]}.{code[2:]}"

            # 查询并保存分红数据
            for year in range(first_year, year_now + 1):
                try:
                    result_set = bs.query_dividend_data(
                        code=formatted_code, 
                        year=str(year), 
                        yearType="operate"
                    )
                    
                    while result_set.error_code == "0" and result_set.next():
                        data = result_set.get_row_data()
                        
                        # 解析分红数据
                        dividend_date = data[6]
                        cash = _safe_float(data[9])
                        reserve = _safe_float(data[11])
                        stock = _safe_float(data[13])
         
                        # 如果该日期不在已有列表中,也不在前后指定天数范围内,且不晚于今天,则创建
                        if not self.__is_date_near_existing(dividend_date, date_set, today):
                            Operation.objects.create(
                                date=dividend_date,
                                code=code,
                                operationType=OPERATION_TYPE_DIVIDEND,
                                cash=cash,
                                reserve=reserve,
                                stock=stock,
                            )
                            update_count += 1
                            # 将新日期添加到已有日期集合中
                            date_set.add(dividend_date)
                            
                except Exception as e:
                    logger.error(f"查询股票 {code} 第 {year} 年分红数据失败: {e}")
                    continue

            # 更新分红记录的持仓数量
            update_count -= self.__update_dividend_holdings(code)

            return name if update_count > 0 else ""
            
        except Exception as e:
            logger.error(f"生成股票 {code} 分红信息失败: {e}")
            return ""
    
    def __update_dividend_holdings(self, code: str) -> int:
        """更新分红记录的持仓数量并删除无效记录"""
        operations = Operation.objects.filter(code=code).order_by("date")
        current_hold = 0
        deleted_count = 0
        
        for operation in operations:
            # 根据操作类型更新持仓
            if operation.operationType == OPERATION_TYPE_BUY:
                current_hold += operation.count
            elif operation.operationType == OPERATION_TYPE_SELL:
                current_hold -= operation.count
            elif operation.operationType == OPERATION_TYPE_DIVIDEND:
                # 如果分红时没有持仓,删除该分红记录
                if current_hold == 0:
                    operation.delete()
                    deleted_count += 1
                else:
                    # 更新分红记录的持仓数量
                    operation.count = current_hold
                    operation.save()
                    # 分红后更新持仓(送股和转增)
                    current_hold += current_hold * (operation.reserve + operation.stock)
        
        return deleted_count


    # 计算个股指标
    def __caculate_single_target(self, key):
        if key is None:
            return ""
        to_return = {}

        # 带上股票的标签（优化：使用字典查找，O(1) 复杂度）
        stock_meta = self.stockMeta_dict.get(key)
        if stock_meta:
            to_return["stockType"] = stock_meta.stockType
            to_return["isNew"] = stock_meta.isNew

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

        # 优化：一次遍历计算所有指标
        metrics = self.__caculate_single_metrics_optimized(single_operation_list)
        
        current_hold_count = metrics['current_hold_count']
        yesterday_hold_count = metrics['yesterday_hold_count']
        current_hold_cost = metrics['current_hold_cost']
        current_overall = metrics['current_overall']
        today_input = metrics['today_input']
        total_fee = metrics['total_fee']
        holding_duration = metrics['holding_duration']
        
        to_return["holdCount"] = current_hold_count  # 持股数
        to_return["holdCost"] = current_hold_cost  # 持仓成本
        to_return["overallCost"] = (
            current_overall / current_hold_count if current_hold_count > 0 else 0
        )  # 摊薄成本
        to_return["totalValue"] = (
            float(single_real_time[1]) * current_hold_count
        )  # 今日市值
        to_return["totalValueYesterday"] = (
            float(single_real_time[4]) * yesterday_hold_count
        )  # 昨日市值,不显示

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

        to_return["totalCost"] = total_fee  # 所有费用

        total_offset_today = 0
        if to_return["totalValueYesterday"] < 0.1:
            total_offset_today = current_offset  # 今天新买的,今日盈亏等于浮动盈亏
        else:
            total_offset_today = (
                float(single_real_time[1]) * current_hold_count
                - float(single_real_time[4]) * yesterday_hold_count
                - today_input
            )

        to_return["totalOffsetToday"] = total_offset_today  # 今日盈亏,不显示
        
        # 持股时长（已在 metrics 中计算）
        to_return["holdingDuration"] = holding_duration

        to_return["operationList"] = self.__caculate_single_operation_list(
            single_operation_list
        )

        return to_return

    def __caculate_single_metrics_optimized(self, single_operation_list: List) -> Dict:
        """
        优化：一次遍历计算所有指标
        合并了原来的多个方法：
        - __caculate_single_holdCount (今天和昨天)
        - __caculate_single_hold_cost
        - __caculate_single_overall
        - __caculate_single_today_input
        - __caculate_single_fee
        - __caculate_holding_duration (持股时长)
        
        Args:
            single_operation_list: 操作记录列表
            
        Returns:
            Dict: 包含所有计算指标的字典
        """
        # 获取今天的日期（只调用一次）
        today = self._today
        
        # 初始化所有累计变量
        current_hold = 0.0  # 当前持股数
        yesterday_hold = 0.0  # 昨日持股数
        
        # 持仓成本相关
        hold_total_pay = 0.0  # 持仓总支付（用于计算持仓成本）
        hold_total_count = 0.0  # 持仓总数量
        
        # 摊薄成本相关
        overall_sum = 0.0  # 摊薄成本总和
        
        # 其他指标
        today_input = 0.0  # 今日净投入
        total_fee = 0.0  # 总手续费
        
        # 持股时长相关
        holding_start_date = None  # 当前持仓周期的开始日期
        total_holding_days = 0  # 累计持股天数
        
        for operation in single_operation_list:
            op_type = operation.operationType
            
            # 累计手续费
            total_fee += operation.fee
            
            # 判断是否是今天的操作
            is_today = operation.date == today
            
            if op_type == OPERATION_TYPE_BUY:
                # 买入操作
                previous_hold = current_hold
                current_hold += operation.count
                
                # 持仓成本计算
                hold_total_pay += operation.count * operation.price + operation.fee
                hold_total_count += operation.count
                
                # 摊薄成本计算
                overall_sum += operation.count * operation.price + operation.fee
                
                # 今日投入计算
                if is_today:
                    today_input += operation.count * operation.price + operation.fee
                
                # 持股时长计算：如果之前没有持仓，现在买入后持股数 >= 1，记录开始日期
                if previous_hold < 1 and current_hold >= 1:
                    holding_start_date = operation.date
                    
            elif op_type == OPERATION_TYPE_SELL:
                # 卖出操作
                previous_hold = current_hold
                current_hold -= operation.count
                
                # 摊薄成本计算
                overall_sum -= operation.count * operation.price - operation.fee
                
                # 今日投入计算（卖出是负投入）
                if is_today:
                    today_input -= operation.count * operation.price + operation.fee
                
                # 持股时长计算：如果卖出后持股数 < 1，结算这一轮的持股时长
                if previous_hold >= 1 and current_hold < 1:
                    if holding_start_date:
                        duration = (operation.date - holding_start_date).days
                        total_holding_days += duration
                        holding_start_date = None
                
                # 如果清仓了，重置持仓成本相关变量
                if current_hold == 0:
                    hold_total_pay = 0.0
                    hold_total_count = 0.0
                    
            elif op_type == OPERATION_TYPE_DIVIDEND:
                # 分红操作
                dividend_multiplier = operation.reserve + operation.stock
                
                # 持仓成本计算
                hold_total_count += hold_total_count * dividend_multiplier
                
                # 摊薄成本计算
                overall_sum -= current_hold * operation.cash
                
                # 更新持股数（送股和转增）
                current_hold += current_hold * dividend_multiplier
            
            # 计算昨日持股数（在处理完当前操作后）
            if not is_today:
                yesterday_hold = current_hold
        
        # 如果当前仍在持有（持股数 >= 1），计算到今天的时长
        if current_hold >= 1 and holding_start_date:
            duration = (today - holding_start_date).days
            total_holding_days += duration
        
        # 计算持仓成本
        current_hold_cost = hold_total_pay / hold_total_count if hold_total_count > 0 else 0.0
        
        return {
            'current_hold_count': current_hold,
            'yesterday_hold_count': yesterday_hold,
            'current_hold_cost': current_hold_cost,
            'current_overall': overall_sum,
            'today_input': today_input,
            'total_fee': total_fee,
            'holding_duration': total_holding_days,
        }

    def __caculate_single_operation_list(self, single_operation_list):
        """将操作列表转换为字典列表并反转顺序"""
        return [op.to_dict() for op in reversed(single_operation_list)]

    def __caculate_single_holdCount(self, single_operation_list: List, yesterday: int = 0) -> float:
        """
        计算某个股票当前持股数
        
        Args:
            single_operation_list: 操作记录列表（假设已按时间排序）
            yesterday: 1表示只计算到昨天的持仓，0表示计算到今天
            
        Returns:
            float: 持股数量
        """
        current_hold = 0
        # 在方法开始时获取today并赋值给局部变量
        today = self._today
        
        for single_operation in single_operation_list:
            if yesterday == 1:
                # 只计算到昨天的持仓
                if single_operation.date >= today:
                    continue

            if single_operation.operationType == OPERATION_TYPE_BUY:
                current_hold += single_operation.count
            elif single_operation.operationType == OPERATION_TYPE_SELL:
                current_hold -= single_operation.count
            elif single_operation.operationType == OPERATION_TYPE_DIVIDEND:
                current_hold += current_hold * (
                    single_operation.reserve + single_operation.stock
                )

        return current_hold


    def __caculate_overall_target(self, single_target_list: List[Dict]) -> Dict:
        """
        计算整体指标
        
        Args:
            single_target_list: 个股指标列表
            
        Returns:
            Dict: 整体指标字典
        """
        to_return = {}

        # 获取基础数据
        origin_cash_set = Info.objects.filter(key=INFO_KEY_ORIGIN_CASH).first()
        income_cash_set = Info.objects.filter(key=INFO_KEY_INCOME_CASH).first()
        
        origin_cash = float(origin_cash_set.value) if origin_cash_set else 0.0
        income_cash = float(income_cash_set.value) if income_cash_set else 0.0

        # 使用 sum() 简化累加
        current_offset = sum(target["offsetCurrent"] for target in single_target_list)
        total_offset = sum(target["offsetTotal"] for target in single_target_list)
        total_value = sum(target["totalValue"] for target in single_target_list)
        total_offset_today = sum(target["totalOffsetToday"] for target in single_target_list)
        total_cost = sum(target["totalCost"] for target in single_target_list)

        # 计算整体指标
        to_return["offsetCurrent"] = current_offset  # 浮动盈亏
        to_return["offsetTotal"] = total_offset + income_cash  # 累计盈亏
        to_return["totalValue"] = total_value  # 总市值
        to_return["offsetCurrentRatio"] = f"{(current_offset / total_value * 100) if total_value > 0 else 0:.2f}%"  # 浮动盈亏率
        to_return["offsetToday"] = total_offset_today  # 今日盈亏
        to_return["totalCash"] = origin_cash + total_offset + income_cash - total_value  # 总现金
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
浮动盈亏额 = (当前价 - 持仓成本) * 多仓持股数
浮动盈亏率 = 浮动盈亏额 / (持仓成本价 * 持股数)
分市场浮动盈亏额 = ∑个股浮动盈亏额
分市场浮动盈亏率 = 分市场浮动盈亏额 / ∑(个股持仓成本 * 个股持股数)
3、累计盈亏
个股累计盈亏额 = 多仓市值 - (∑买入金额 - ∑卖出金额 - ∑现金股息) 
个股累计盈亏率 = 累计盈亏额 / ∑买入金额
分市场累计盈亏额 = ∑个股累计盈亏额
无银转
分市场累计盈亏率 = 累计盈亏额 / ∑个股买入金额
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
code, name,priceNow,offsetToday,offsetTodayRatio,totalValue,holdCount,holdCost,overallCost,offsetCurrent,offsetCurrentRatio,offsetTotal

整体指标
offsetToday,offsetCurrent,offsetCurrentRatio,offsetTotal,totalValue,totalCash,originCash
"""
