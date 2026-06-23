"""关注列表拼装：DB 配置 + 行情/估值/历史高 → WatchResultItem（纯计算，无 I/O）"""
from backend.common.types import (
    OperationDict,
    RealtimePriceDict,
    ValuationData,
    WatchItemDict,
    WatchResultItem,
)
from backend.common.utils import extract_offset_today
from backend.services.calculation.constants import MIN_PRICE_THRESHOLD
from backend.services.calculation.single_metrics import compute_single_metrics


def _ratio(price: float | None, per_share: float | None) -> float | None:
    if price and per_share:
        return round(price / per_share, 2)
    return None


def build_holding_offset(
    holding_set: set[str],
    operation_list: OperationDict,
    prices: RealtimePriceDict,
) -> dict[str, float]:
    """根据最新现价与用户账本，计算已持仓股票的累计盈亏（offsetTotal）。"""
    offset: dict[str, float] = {}
    for code in holding_set:
        operations = operation_list.get(code) or []
        if not operations:
            continue
        metrics = compute_single_metrics(operations)
        if not metrics.is_holding():
            continue
        price_data = prices.get(code) or {}
        price_now = price_data.get("currentPrice")
        if price_now is None or price_now < MIN_PRICE_THRESHOLD:
            continue
        offset[code] = metrics.offset_total(price_now)
    return offset


def build_watchlist(
    items: list[WatchItemDict],
    prices: RealtimePriceDict,
    valuations: dict[str, ValuationData],
    hist_highs: dict[str, float | None],
    holding_set: set[str],
    holding_offset: dict[str, float] | None = None,
) -> list[WatchResultItem]:
    result: list[WatchResultItem] = []
    for item in items:
        code = item["code"]
        price_data = prices.get(code, {})
        valuation = valuations.get(code, {})
        price_now = price_data.get("currentPrice") if price_data else None
        offset_today, offset_today_ratio = extract_offset_today(price_now, price_data)
        entry = WatchResultItem(
            code=code,
            name=(price_data.get("name") if price_data else None) or code,
            holding=code in holding_set,
            priceNow=price_now,
            offsetToday=offset_today,
            offsetTodayRatio=offset_today_ratio,
            histHigh=hist_highs.get(code),
            pe=_ratio(price_now, valuation.get("epsTtm")),
            pb=_ratio(price_now, valuation.get("bvps")),
            risk=item["risk"] or "",
            opportunity=item["opportunity"] or "",
            leftPoint=item["leftPoint"],
            trendPoint=item["trendPoint"],
            bloodPoint=item["bloodPoint"],
        )
        if holding_offset and code in holding_offset:
            entry["offsetTotal"] = holding_offset[code]
        result.append(entry)
    return result
