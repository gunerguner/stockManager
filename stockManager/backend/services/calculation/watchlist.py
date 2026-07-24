"""关注列表拼装：DB 配置 + 行情/估值/历史高 → WatchResultItem（纯计算，无 I/O）"""
from backend.common.types import (
    RealtimePriceDict,
    ValuationData,
    WatchItemDict,
    WatchResultItem,
)
from backend.common.utils import extract_offset_today


def _ratio(price: float | None, per_share: float | None) -> float | None:
    if price and per_share:
        return round(price / per_share, 2)
    return None


def build_watchlist(
    items: list[WatchItemDict],
    prices: RealtimePriceDict,
    valuations: dict[str, ValuationData],
    hist_highs: dict[str, float | None],
) -> list[WatchResultItem]:
    result: list[WatchResultItem] = []
    for item in items:
        code = item["code"]
        price_data = prices.get(code, {})
        valuation = valuations.get(code, {})
        price_now = price_data.get("currentPrice") if price_data else None
        offset_today, offset_today_ratio = extract_offset_today(price_now, price_data)
        result.append(WatchResultItem(
            code=code,
            name=(price_data.get("name") if price_data else None) or code,
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
            hidden=bool(item.get("hidden", False)),
        ))
    return result
