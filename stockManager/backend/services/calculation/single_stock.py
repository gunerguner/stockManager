"""单股指标拼装：行情 + 账本 metrics → StockData

港股通个股金额与价格为港币（HKD），不做汇率换算；组合汇总见 overall.py。
"""
from backend.common import logger
from backend.common.types import RealtimePriceData, StockData
from backend.models import Operation, StockMeta as StockMetaModel
from backend.services.calculation.constants import MIN_PRICE_THRESHOLD
from backend.services.calculation.money_weighted import calculate_money_weighted_return
from backend.services.calculation.single_metrics import SingleStockMetrics, compute_single_metrics


def _resolve_stock_name(
    code: str,
    single_real_time: RealtimePriceData,
    stock_meta: StockMetaModel | None = None,
) -> str:
    """优先展示实时接口名称，其次回退 StockMeta 名称。"""
    realtime_name = (single_real_time.get("name") or "").strip()
    if realtime_name:
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
        "yearHigh": None,
    })


def attach_price_fields(
    code: str,
    single_real_time: RealtimePriceData,
    stock_meta: StockMetaModel | None,
) -> dict:
    price_now = single_real_time["currentPrice"]
    return {
        "code": code,
        **({"stockType": stock_meta.stockType, "isNew": stock_meta.isNew} if stock_meta else {}),
        "name": _resolve_stock_name(code, single_real_time, stock_meta),
        "priceNow": price_now,
        **(
            {"offsetToday": 0.0, "offsetTodayRatio": 0.0}
            if price_now < MIN_PRICE_THRESHOLD
            else {"offsetToday": single_real_time["priceOffset"], "offsetTodayRatio": single_real_time["offsetRatio"]}
        ),
    }


def attach_hold_fields(
    single_real_time: RealtimePriceData,
    metrics: SingleStockMetrics,
) -> dict:
    current_price = single_real_time["currentPrice"]
    return {
        "holdCount": metrics.current_hold_count,
        "holdCost": metrics.current_hold_cost,
        "overallCost": metrics.overall_cost_per_share(),
        "totalValue": current_price * metrics.current_hold_count,
        "totalValueYesterday": single_real_time["yesterdayClose"] * metrics.yesterday_hold_count,
    }


def attach_pnl_fields(
    single_real_time: RealtimePriceData,
    metrics: SingleStockMetrics,
    operations: list[Operation],
    total_value_yesterday: float,
) -> dict:
    current_price = single_real_time["currentPrice"]
    offset_total = metrics.offset_total(current_price)

    return {
        "offsetCurrent": metrics.offset_current(current_price),
        "offsetCurrentRatio": metrics.offset_current_ratio(current_price),
        "offsetTotal": offset_total,
        "moneyWeightedReturn": calculate_money_weighted_return(operations, offset_total),
        "totalCost": metrics.total_fee,
        "totalOffsetToday": metrics.offset_today(
            current_price,
            single_real_time["yesterdayClose"],
            total_value_yesterday,
        ),
        "holdingDuration": metrics.holding_duration,
    }


def build_single_stock(
    code: str,
    operations: list[Operation],
    single_real_time: RealtimePriceData | None,
    stock_meta: StockMetaModel | None = None,
) -> StockData:
    """计算单个股票的指标"""
    if not single_real_time:
        logger.warning(f"无法获取股票 {code} 的实时价格")
        single_real_time = _default_realtime_price()

    metrics = compute_single_metrics(operations)

    result: StockData = {}
    result.update(attach_price_fields(code, single_real_time, stock_meta))
    result.update(attach_hold_fields(single_real_time, metrics))
    result.update(attach_pnl_fields(
        single_real_time,
        metrics,
        operations,
        result["totalValueYesterday"],
    ))
    return result
