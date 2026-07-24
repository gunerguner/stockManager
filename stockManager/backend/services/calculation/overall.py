"""组合整体指标与 XIRR 计算

个股金额类字段已统一为人民币（CNY）；本模块直接汇总，不再对港股二次乘汇率。
"""
import datetime
from typing import cast

from pyxirr import xirr

from backend.common import logger
from backend.common.types import CashFlowList, OverallData, StockData


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
    hkd_cny_rate: float = 0.86,
) -> OverallData:
    """计算整体指标（个股金额已为 CNY，直接相加）。"""
    to_return = cast(OverallData, {})

    current_offset = sum(t.get("offsetCurrent", 0.0) for t in stock_list)
    total_offset = sum(t.get("offsetTotal", 0.0) for t in stock_list)
    total_value = sum(t.get("totalValue", 0.0) for t in stock_list)
    total_offset_today = sum(t.get("totalOffsetToday", 0.0) for t in stock_list)
    total_cost = sum(t.get("totalCost", 0.0) for t in stock_list)

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
    to_return["xirrAnnualized"] = xirr_rate

    to_return["cashFlowList"] = [
        {
            "date": flow["date"],
            "amount": flow["amount"],
        }
        for flow in cash_flow_list
    ]

    to_return["hkdCnyRate"] = hkd_cny_rate

    return to_return
