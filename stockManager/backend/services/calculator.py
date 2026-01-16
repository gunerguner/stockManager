"""
股票计算器模块
提供股票指标计算功能，包括单股指标和整体指标计算
"""
import datetime
from typing import Any, Dict, List, Optional

from pyxirr import xirr

from ..common import logger
from ..common.constants import OperationType
from ..models import Operation
from .stockMeta import StockMeta
from .realtimePrice import RealtimePrice, RealtimePriceData

# ========== 常量定义 ==========
MIN_PRICE_THRESHOLD = 0.001  # 最小价格阈值，低于此值认为价格无效
MIN_VALUE_THRESHOLD = 0.1  # 最小市值阈值，用于判断昨日市值是否有效
MIN_HOLD_COUNT_THRESHOLD = 0.001  # 最小持股数阈值，用于浮点数比较


class Calculator:
    """
    股票计算器类
    
    负责计算股票相关的各项指标，包括：
    - 单股指标：持仓成本、浮动盈亏、累计盈亏等
    - 整体指标：总市值、总盈亏、总资产等
    """
    
    # ========== 公共接口 ==========
    
    @classmethod
    def calculate_target(cls, operation_list: Dict[str, List[Operation]], income_cash: float = 0.0, cash_flow_list: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        code_list = list(operation_list.keys())
        realtime_price_list = RealtimePrice.query(code_list)
        stock_list = [
            cls._calculate_single_target(operation_list, key, realtime_price_list.get(key))
            for key in operation_list.keys()
        ]
        return {
            "stocks": stock_list,
            "overall": cls._calculate_overall_target(stock_list, income_cash, cash_flow_list or [])
        }
    
    # ========== 单股计算 ==========
    
    @classmethod
    def _calculate_single_target(cls, operation_list: Dict[str, List[Operation]], key: str, single_real_time: Optional[RealtimePriceData]) -> Dict[str, Any]:
        """计算单个股票的指标"""
        to_return = {}

        # 带上股票的标签
        stock_meta = StockMeta.get(key)
        if stock_meta:
            to_return["stockType"] = stock_meta.stockType
            to_return["isNew"] = stock_meta.isNew

        single_operation_list = operation_list[key]
        if not single_real_time:
            logger.warning(f"无法获取股票 {key} 的实时价格")
            # 使用默认值
            single_real_time = RealtimePriceData("未知", 0.0, 0.0, "0%", 0.0)

        to_return["code"] = key
        to_return["name"] = single_real_time.name  # 名称
        to_return["priceNow"] = single_real_time.currentPrice  # 现价（已经是 float）
        if to_return["priceNow"] < MIN_PRICE_THRESHOLD:
            to_return["offsetToday"] = 0  # 今日股价涨跌
            to_return["offsetTodayRatio"] = "0%"  # 今日涨跌率
        else:
            to_return["offsetToday"] = single_real_time.priceOffset  # 今日股价涨跌
            to_return["offsetTodayRatio"] = single_real_time.offsetRatio  # 今日涨跌率

        metrics = cls._calculate_single_metrics_optimized(single_operation_list)
        
        current_hold_count = metrics['current_hold_count']
        yesterday_hold_count = metrics['yesterday_hold_count']
        current_hold_cost = metrics['current_hold_cost']
        current_overall = metrics['current_overall']
        today_input = metrics['today_input']
        total_fee = metrics['total_fee']
        holding_duration = metrics['holding_duration']
        
        to_return["holdCount"] = current_hold_count  # 持股数
        to_return["holdCost"] = current_hold_cost  # 持仓成本
        # 摊薄成本：使用更严格的浮点数比较，避免除零错误
        to_return["overallCost"] = (
            current_overall / current_hold_count 
            if abs(current_hold_count) >= MIN_HOLD_COUNT_THRESHOLD 
            else 0.0
        )
        to_return["totalValue"] = (
            single_real_time.currentPrice * current_hold_count
        )  # 今日市值
        to_return["totalValueYesterday"] = (
            single_real_time.yesterdayClose * yesterday_hold_count
        )  # 昨日市值,不显示

        current_offset = (
            single_real_time.currentPrice - current_hold_cost
        ) * current_hold_count
        to_return["offsetCurrent"] = current_offset  # 浮动盈亏额
        # 浮动盈亏率：使用更严格的浮点数比较，避免除零错误
        current_offset_ratio = (
            (single_real_time.currentPrice - current_hold_cost) / current_hold_cost
            if abs(current_hold_cost) >= MIN_PRICE_THRESHOLD
            else 0.0
        )
        to_return["offsetCurrentRatio"] = "%.2f%%" % (
            current_offset_ratio * 100
        )  # 浮动盈亏率

        to_return["offsetTotal"] = (
            single_real_time.currentPrice * current_hold_count - current_overall
        )  # 累计盈亏额

        to_return["totalCost"] = total_fee  # 所有费用

        total_offset_today = 0.0
        # 使用常量判断昨日市值是否有效，消除魔法数字
        if to_return["totalValueYesterday"] < MIN_VALUE_THRESHOLD:
            total_offset_today = current_offset  # 今天新买的,今日盈亏等于浮动盈亏
        else:
            total_offset_today = (
                single_real_time.currentPrice * current_hold_count
                - single_real_time.yesterdayClose * yesterday_hold_count
                - today_input
            )

        to_return["totalOffsetToday"] = total_offset_today  # 今日盈亏,不显示
        
        # 持股时长（已在 metrics 中计算）
        to_return["holdingDuration"] = holding_duration

        to_return["operationList"] = [op.to_dict() for op in reversed(single_operation_list)]

        return to_return
    
    @classmethod
    def _calculate_single_metrics_optimized(cls, single_operation_list: List[Operation]) -> Dict[str, Any]:
        """一次遍历计算所有指标"""
        today = datetime.date.today()
        
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
            
            if op_type == OperationType.BUY:
                # 买入操作：
                
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
                    
            elif op_type == OperationType.SELL:
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
                    
            elif op_type == OperationType.DIVIDEND:
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
        
        # 计算持仓成本：使用更严格的浮点数比较，避免除零错误
        current_hold_cost = (
            hold_total_pay / hold_total_count 
            if abs(hold_total_count) >= MIN_HOLD_COUNT_THRESHOLD 
            else 0.0
        )
        

        
        return {
            'current_hold_count': current_hold,
            'yesterday_hold_count': yesterday_hold,
            'current_hold_cost': current_hold_cost,
            'current_overall': overall_sum,
            'today_input': today_input,
            'total_fee': total_fee,
            'holding_duration': total_holding_days,
        }
    
    # ========== 整体计算 ==========
    
    @classmethod
    def _calculate_xirr(cls, cash_flow_list: List[Dict[str, Any]], total_asset: float) -> float:
        """
        计算 XIRR 年化收益率
        
        Args:
            cash_flow_list: 出入金记录列表 [{"date": "2023-01-01", "amount": 10000}, ...]
            total_asset: 当前总资产（作为最后一笔正现金流）
        
        Returns:
            XIRR 年化收益率（小数形式，如 0.1234 代表 12.34%）
        """
        # 边界情况：没有现金流记录
        if not cash_flow_list:
            logger.info("没有现金流记录，XIRR 返回 0")
            return 0.0
        
        try:
            # 构建日期和金额列表
            dates = []
            amounts = []
            
            # 将所有现金流记录添加到列表中
            # 入金为负（投出去），出金为正（收回来）
            for flow in cash_flow_list:
                date_str = flow.get('date')
                amount = flow.get('amount', 0)
                
                # 跳过金额为 0 的记录
                if amount == 0:
                    continue
                
                # 解析日期
                if isinstance(date_str, str):
                    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                else:
                    date_obj = date_str
                
                dates.append(date_obj)
                # 转换现金流方向：入金为负，出金为正
                # 数据库中 amount > 0 是入金，amount < 0 是出金
                amounts.append(float(-amount))
            
            # 边界情况：处理后没有有效现金流
            if not dates:
                logger.info("没有有效的现金流记录，XIRR 返回 0")
                return 0.0
            
            # 添加当前总资产作为最后一笔正现金流（假设今天全部赎回）
            today = datetime.date.today()
            dates.append(today)
            amounts.append(float(total_asset))
            
            # 检查是否有正负现金流（XIRR 必须有资金流入和流出）
            has_positive = any(amt > 0 for amt in amounts)
            has_negative = any(amt < 0 for amt in amounts)
            
            if not (has_positive and has_negative):
                logger.info("现金流没有正负两种方向，XIRR 无意义，返回 0")
                return 0.0
            
            # 调用 pyxirr 计算 XIRR
            result = xirr(dates, amounts)
            
            # pyxirr 可能返回 None
            if result is None:
                logger.warning("XIRR 计算返回 None，可能不收敛")
                return 0.0
            
            return float(result)
            
        except Exception as e:
            logger.error(f"XIRR 计算失败: {str(e)}", exc_info=True)
            return 0.0
    
    @classmethod
    def _calculate_overall_target(cls, single_target_list: List[Dict[str, Any]], income_cash: float, cash_flow_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算整体指标"""
        to_return = {}

        # 使用 sum() 简化累加
        current_offset = sum(target["offsetCurrent"] for target in single_target_list)
        total_offset = sum(target["offsetTotal"] for target in single_target_list)
        total_value = sum(target["totalValue"] for target in single_target_list)
        total_offset_today = sum(target["totalOffsetToday"] for target in single_target_list)
        total_cost = sum(target["totalCost"] for target in single_target_list)

        # 从 cash_flow_list 计算总入金（所有 amount 的总和）
        origin_cash = sum(flow['amount'] for flow in cash_flow_list)

        # 计算整体指标
        to_return["offsetCurrent"] = current_offset  # 浮动盈亏
        to_return["offsetTotal"] = total_offset + income_cash  # 累计盈亏
        to_return["totalValue"] = total_value  # 总市值
        to_return["offsetToday"] = total_offset_today  # 今日盈亏
        to_return["totalCash"] = origin_cash + total_offset + income_cash - total_value  # 总现金
        to_return["totalAsset"] = origin_cash + total_offset + income_cash  # 总资产
        to_return["totalCost"] = total_cost  # 总费用
        to_return["incomeCash"] = income_cash  # 逆回购等收入
        to_return["originCash"] = origin_cash  # 总入金（从 cash_flow_list 计算）
        
        # 计算 XIRR 年化收益率
        total_asset = to_return["totalAsset"]
        xirr_rate = cls._calculate_xirr(cash_flow_list, total_asset)
        to_return["xirrAnnualized"] = f"{(xirr_rate * 100):.2f}%"  # XIRR 年化收益率
        
        # 将 cash_flow_list 转换为前端需要的格式（date, amount）
        to_return["cashFlowList"] = [
            {
                "date": flow["date"],
                "amount": flow["amount"],
            }
            for flow in cash_flow_list
        ]

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
offsetToday,offsetCurrent,offsetTotal,totalValue,totalCash,totalAsset,originCash,incomeCash,xirrAnnualized
"""
