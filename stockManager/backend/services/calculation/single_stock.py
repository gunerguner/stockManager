"""单股指标拼装：行情 + 账本 metrics → StockData"""
from ...common import logger
from ...common.types import RealtimePriceData, StockData
from ...models import Operation, StockMeta as StockMetaModel
from .constants import MIN_HOLD_COUNT_THRESHOLD, MIN_PRICE_THRESHOLD, MIN_VALUE_THRESHOLD
from .money_weighted import calculate_money_weighted_return
from .single_metrics import SingleStockMetrics, compute_single_metrics


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
        "offsetRatio": "0%",
        "yesterdayClose": 0.0,
    })


def attach_price_fields(
    code: str,
    single_real_time: RealtimePriceData,
    stock_meta: StockMetaModel | None,
) -> dict:
    fields: dict = {"code": code}
    if stock_meta:
        fields["stockType"] = stock_meta.stockType
        fields["isNew"] = stock_meta.isNew
    fields["name"] = _resolve_stock_name(code, single_real_time, stock_meta)
    fields["priceNow"] = single_real_time["currentPrice"]
    if fields["priceNow"] < MIN_PRICE_THRESHOLD:
        fields["offsetToday"] = 0
        fields["offsetTodayRatio"] = "0%"
    else:
        fields["offsetToday"] = single_real_time["priceOffset"]
        fields["offsetTodayRatio"] = single_real_time["offsetRatio"]
    return fields


def attach_hold_fields(
    single_real_time: RealtimePriceData,
    metrics: SingleStockMetrics,
) -> dict:
    current_price = single_real_time["currentPrice"]
    hold_count = metrics.current_hold_count
    return {
        "holdCount": hold_count,
        "holdCost": metrics.current_hold_cost,
        "overallCost": (
            metrics.current_overall / hold_count
            if abs(hold_count) >= MIN_HOLD_COUNT_THRESHOLD
            else 0.0
        ),
        "totalValue": current_price * hold_count,
        "totalValueYesterday": single_real_time["yesterdayClose"] * metrics.yesterday_hold_count,
    }


def _compute_total_offset_today(
    single_real_time: RealtimePriceData,
    metrics: SingleStockMetrics,
    current_offset: float,
    total_value_yesterday: float,
) -> float:
    if total_value_yesterday < MIN_VALUE_THRESHOLD:
        return current_offset
    return (
        single_real_time["currentPrice"] * metrics.current_hold_count
        - single_real_time["yesterdayClose"] * metrics.yesterday_hold_count
        - metrics.today_input
    )


def attach_pnl_fields(
    single_real_time: RealtimePriceData,
    metrics: SingleStockMetrics,
    operations: list[Operation],
    total_value_yesterday: float,
) -> dict:
    current_price = single_real_time["currentPrice"]
    hold_count = metrics.current_hold_count
    hold_cost = metrics.current_hold_cost

    current_offset = (current_price - hold_cost) * hold_count
    current_offset_ratio = (
        (current_price - hold_cost) / hold_cost
        if abs(hold_cost) >= MIN_PRICE_THRESHOLD
        else 0.0
    )
    offset_total = current_price * hold_count - metrics.current_overall

    return {
        "offsetCurrent": current_offset,
        "offsetCurrentRatio": "%.2f%%" % (current_offset_ratio * 100),
        "offsetTotal": offset_total,
        "moneyWeightedReturn": calculate_money_weighted_return(operations, offset_total),
        "totalCost": metrics.total_fee,
        "totalOffsetToday": _compute_total_offset_today(
            single_real_time, metrics, current_offset, total_value_yesterday
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
