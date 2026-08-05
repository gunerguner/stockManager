"""关注列表用例：展示拼装与隐藏设置"""
from django.contrib.auth.models import User

from backend.common import logger
from backend.common.types import (
    RealtimePriceDict,
    ValuationData,
    WatchItemDict,
    WatchResultItem,
)
from backend.common.utils import extract_offset_today, safe_ratio
from backend.models import WatchItem


class Watchlist:
    """关注列表：拼装展示与隐藏开关。"""

    @classmethod
    def build(
        cls,
        items: list[WatchItemDict],
        prices: RealtimePriceDict,
        valuations: dict[str, ValuationData],
        hist_highs: dict[str, float | None],
    ) -> list[WatchResultItem]:
        """关注配置 + 行情/估值/历史高 → 展示列表。"""
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
                pe=safe_ratio(price_now, valuation.get("epsTtm")),
                pb=safe_ratio(price_now, valuation.get("bvps")),
                risk=item["risk"] or "",
                opportunity=item["opportunity"] or "",
                leftPoint=item["leftPoint"],
                trendPoint=item["trendPoint"],
                bloodPoint=item["bloodPoint"],
                hidden=bool(item.get("hidden", False)),
            ))
        return result

    @classmethod
    def set_hidden(cls, user: User, code: str, hidden: bool) -> None:
        """设置关注项隐藏状态。"""
        try:
            item = WatchItem.objects.get(user=user, stock_meta__code=code)
        except WatchItem.DoesNotExist as exc:
            raise WatchItem.DoesNotExist(f"关注项不存在: {code}") from exc
        item.hidden = hidden
        item.save(update_fields=["hidden"])
        logger.info(f"用户 {user.username} 设置关注隐藏: {code}={hidden}")
