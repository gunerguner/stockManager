"""未落库的 Operation / StockMeta 构造，供盈亏单测使用。"""
from datetime import date
from decimal import Decimal

from backend.models import Operation, StockMeta


def make_meta(
    code: str = "sh600519",
    name: str = "贵州茅台",
    stock_type: str = "SH60",
) -> StockMeta:
    return StockMeta(code=code, name=name, stockType=stock_type)


def make_op(
    meta: StockMeta,
    *,
    op_date: date,
    op_type: str = "BUY",
    price: str | float = 0,
    count: int = 0,
    fee: str | float = 0,
    amount: str | float | None = None,
    cash: str | float = 0,
    stock: float = 0,
    reserve: float = 0,
    sort_order: int = 0,
) -> Operation:
    return Operation(
        stock_meta=meta,
        date=op_date,
        sortOrder=sort_order,
        operationType=op_type,
        price=Decimal(str(price)),
        count=count,
        fee=Decimal(str(fee)),
        amount=None if amount is None else Decimal(str(amount)),
        cash=Decimal(str(cash)),
        stock=stock,
        reserve=reserve,
    )


def realtime(
    *,
    name: str = "",
    current: float = 0.0,
    yesterday: float = 0.0,
    offset: float = 0.0,
    ratio: float = 0.0,
) -> dict:
    return {
        "name": name,
        "currentPrice": current,
        "priceOffset": offset,
        "offsetRatio": ratio,
        "yesterdayClose": yesterday,
    }
