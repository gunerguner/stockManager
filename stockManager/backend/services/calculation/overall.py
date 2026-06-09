"""组合整体指标与 XIRR 计算

个股指标为原币种（港股通为 HKD）；本模块汇总时通过 to_cny_amount 折算为人民币（CNY）。
"""
import datetime

from pyxirr import xirr

from ...common import logger
from ...common.market import Market, code_to_market
from ...common.types import CashFlowList, OverallData, StockData
from ...common.utils import format_percent


def to_cny_amount(code: str, amount: float, hkd_cny_rate: float) -> float:
    if code_to_market(code) == Market.HK:
        return amount * hkd_cny_rate
    return amount


def calculate_xirr(cash_flow_list: CashFlowList, total_asset: float) -> float:
    """计算 XIRR 年化收益率"""
    if not cash_flow_list:
        return 0.0

    try:
        pairs = [
            (
                datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                if isinstance(date_str, str)
                else date_str,
                float(-amount),
            )
            for flow in cash_flow_list
            if (amount := flow.get('amount', 0))
            and (date_str := flow.get('date'))
        ]

        if not pairs:
            return 0.0

        dates, amounts = map(list, zip(*pairs))
        dates.append(datetime.date.today())
        amounts.append(float(total_asset))

        if not (any(amt > 0 for amt in amounts) and any(amt < 0 for amt in amounts)):
            return 0.0

        result = xirr(dates, amounts)
        return float(result) if result is not None else 0.0

    except Exception as e:
        logger.error(f"XIRR 计算失败: {str(e)}", exc_info=True)
        return 0.0


def compute_overall(
    stock_list: list[StockData],
    income_cash: float,
    cash_flow_list: CashFlowList,
    hkd_cny_rate: float = 1.0,
) -> OverallData:
    """计算整体指标（港股金额按汇率折算为 CNY）"""
    to_return: OverallData = {}

    def cny(code: str, amount: float) -> float:
        return to_cny_amount(code, amount, hkd_cny_rate)

    current_offset = sum(cny(t["code"], t["offsetCurrent"]) for t in stock_list)
    total_offset = sum(cny(t["code"], t["offsetTotal"]) for t in stock_list)
    total_value = sum(cny(t["code"], t["totalValue"]) for t in stock_list)
    total_offset_today = sum(cny(t["code"], t["totalOffsetToday"]) for t in stock_list)
    total_cost = sum(cny(t["code"], t["totalCost"]) for t in stock_list)

    origin_cash = sum(flow['amount'] for flow in cash_flow_list)

    to_return["offsetCurrent"] = current_offset
    to_return["offsetTotal"] = total_offset + income_cash
    to_return["totalValue"] = total_value
    to_return["offsetToday"] = total_offset_today
    to_return["totalCash"] = origin_cash + total_offset + income_cash - total_value
    to_return["totalAsset"] = origin_cash + total_offset + income_cash
    to_return["totalCost"] = total_cost
    to_return["incomeCash"] = income_cash
    to_return["originCash"] = origin_cash

    total_asset = to_return["totalAsset"]
    xirr_rate = calculate_xirr(cash_flow_list, total_asset)
    to_return["xirrAnnualized"] = format_percent(xirr_rate)

    to_return["cashFlowList"] = [
        {
            "date": flow["date"],
            "amount": flow["amount"],
        }
        for flow in cash_flow_list
    ]

    to_return["hkdCnyRate"] = hkd_cny_rate

    return to_return
