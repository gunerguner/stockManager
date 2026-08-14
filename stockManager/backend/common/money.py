"""金额 Decimal 量化约定（Operation 存储层）"""
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

# price: 覆盖港股 0.001、场内基金 4 位
PRICE_QUANT = Decimal("0.0001")
# fee / amount: 人民币到分
MONEY_QUANT = Decimal("0.01")
# cash: baostock 每股股息常超过 2 位
CASH_QUANT = Decimal("0.000001")


def to_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    """将 float/str/Decimal/None 转为 Decimal；float 经 str 避免二进制尾数。"""
    if value is None:
        return default
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, int):
        return Decimal(value)
    text = str(value).strip()
    if not text:
        return default
    return Decimal(text)


def quantize_price(value: Any) -> Decimal:
    return to_decimal(value).quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)


def quantize_money(value: Any) -> Decimal:
    return to_decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def quantize_cash(value: Any) -> Decimal:
    return to_decimal(value).quantize(CASH_QUANT, rounding=ROUND_HALF_UP)


def decimal_to_float(value: Any | None) -> float | None:
    """API / JSON 边界：Decimal → float；None 保持 None。"""
    if value is None:
        return None
    return float(to_decimal(value))
