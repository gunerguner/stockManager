"""单股指标拼装：行情 + 账本 metrics → StockData

金额类字段统一为人民币（CNY）；港股价格/持仓成本仍为港币。
"""
from typing import cast

from backend.common import logger
from backend.common.domain.market import is_hk_code
from backend.common.types import RealtimePriceData, StockData
from backend.models import Operation, StockMeta as StockMetaModel
from backend.common.thresholds import MIN_QTY
from backend.services.calculation.holdings.money_weighted import calculate_money_weighted_return
from backend.services.calculation.holdings.single_metrics import SingleStockMetrics, compute_single_metrics


def _resolve_stock_name(
    code: str,
    single_real_time: RealtimePriceData,
    stock_meta: StockMetaModel | None = None,
) -> str:
    """优先展示实时接口名称，其次回退 StockMeta 名称。"""
    if realtime_name := (single_real_time.get("name") or "").strip():
        return realtime_name
    if stock_meta and stock_meta.name:
        return stock_meta.name
    return code


def _default_realtime_price() -> RealtimePriceData:
    return RealtimePriceData({
        "name": "",
        "currentPrice": 0.0,
        "priceOffset": 0.0,
        "offsetRatio": 0.0,
        "yesterdayClose": 0.0,
    })


def attach_price_fields(
    code: str,
    single_real_time: RealtimePriceData,
    stock_meta: StockMetaModel | None,
) -> dict:
    current_price = single_real_time["currentPrice"]
    return {
        "code": code,
        **({"stockType": stock_meta.stockType, "isNew": stock_meta.isNew} if stock_meta else {}),
        "name": _resolve_stock_name(code, single_real_time, stock_meta),
        "priceNow": current_price,
        **(
            {"offsetToday": 0.0, "offsetTodayRatio": 0.0}
            if current_price < MIN_QTY
            else {
                "offsetToday": single_real_time["priceOffset"],
                "offsetTodayRatio": single_real_time["offsetRatio"],
            }
        ),
    }


def attach_hold_fields(
    code: str,
    single_real_time: RealtimePriceData,
    metrics: SingleStockMetrics,
    hkd_cny_rate: float,
) -> dict:
    current_price = single_real_time["currentPrice"]
    current_hold_count = metrics.current_hold_count
    yesterday_hold_count = metrics.yesterday_hold_count
    fx = hkd_cny_rate if is_hk_code(code) else 1.0

    return {
        "holdCount": current_hold_count,
        "holdCost": metrics.current_hold_cost,
        "overallCost": metrics.overall_cost_per_share(),
        "totalValue": current_price * current_hold_count * fx,
        "totalValueYesterday": single_real_time["yesterdayClose"] * yesterday_hold_count * fx,
    }


def attach_pnl_fields(
    code: str,
    single_real_time: RealtimePriceData,
    metrics: SingleStockMetrics,
    operations: list[Operation],
    total_value: float,
    total_value_yesterday: float,
    hkd_cny_rate: float,
) -> dict:
    current_price = single_real_time["currentPrice"]
    fx = hkd_cny_rate if is_hk_code(code) else 1.0
    offset_total = metrics.offset_total_cny(total_value)

    return {
        "offsetCurrent": metrics.offset_current_cny(current_price, fx),
        "offsetCurrentRatio": metrics.offset_current_ratio(current_price),
        "offsetTotal": offset_total,
        "moneyWeightedReturn": calculate_money_weighted_return(operations, offset_total),
        "totalCost": metrics.total_fee_cny,
        "totalOffsetToday": metrics.offset_today_cny(
            total_value, total_value_yesterday, current_price, fx
        ),
        "holdingDuration": metrics.holding_duration,
    }


def build_single_stock(
    code: str,
    operations: list[Operation],
    single_real_time: RealtimePriceData | None,
    stock_meta: StockMetaModel | None = None,
    hkd_cny_rate: float = 0.86,
) -> StockData:
    """计算单个股票的指标"""
    if not single_real_time:
        logger.warning(f"无法获取股票 {code} 的实时价格")
        single_real_time = _default_realtime_price()

    metrics = compute_single_metrics(operations, hkd_cny_rate)

    result = cast(StockData, {})
    result.update(attach_price_fields(code, single_real_time, stock_meta))
    result.update(attach_hold_fields(code, single_real_time, metrics, hkd_cny_rate))
    result.update(attach_pnl_fields(
        code,
        single_real_time,
        metrics,
        operations,
        result["totalValue"],
        result["totalValueYesterday"],
        hkd_cny_rate,
    ))
    return result
