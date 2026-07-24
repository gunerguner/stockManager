"""港股通 / A 股交易结算口径：人民币资金账本 + 原币展示账本。"""
from backend.common.market import is_hk_code
from backend.models import Operation


def trade_notional_hkd(operation: Operation) -> float:
    """成交名义金额（港币）：price × count。"""
    return operation.price * operation.count


def trade_amount_cny(operation: Operation) -> float:
    """成交金额（人民币）。港股读 amount；非港股用 price×count。"""
    if is_hk_code(operation.code):
        return float(operation.amount or 0)
    return trade_notional_hkd(operation)


def trade_fee_cny(operation: Operation) -> float:
    """佣金一律按人民币。"""
    return float(operation.fee or 0)


def buy_outflow_cny(operation: Operation) -> float:
    """买入净流出（人民币）= 成交额 + 佣金。"""
    return trade_amount_cny(operation) + trade_fee_cny(operation)


def sell_inflow_cny(operation: Operation) -> float:
    """卖出净流入（人民币）= 成交额 - 佣金。"""
    return trade_amount_cny(operation) - trade_fee_cny(operation)


def implied_fx(operation: Operation) -> float:
    """港股通隐含汇率 amount / (price×count)；无效时返回 0。"""
    if not is_hk_code(operation.code):
        return 1.0
    notional = trade_notional_hkd(operation)
    amount = trade_amount_cny(operation)
    if notional <= 0 or amount <= 0:
        return 0.0
    return amount / notional


def fee_in_price_currency(operation: Operation) -> float:
    """佣金折算到股价币种：港股用隐含汇率折回港币，非港股原样。"""
    fee = trade_fee_cny(operation)
    if not is_hk_code(operation.code):
        return fee
    fx = implied_fx(operation)
    if fx <= 0:
        return 0.0
    return fee / fx


def buy_cost_native(operation: Operation) -> float:
    """买入计入原币成本：price×count + 原币佣金。"""
    return trade_notional_hkd(operation) + fee_in_price_currency(operation)


def sell_proceeds_native(operation: Operation) -> float:
    """卖出原币回款：price×count - 原币佣金。"""
    return trade_notional_hkd(operation) - fee_in_price_currency(operation)


def dividend_cash_cny(operation: Operation, hold: float) -> float:
    """除权现金影响（人民币口径）：持仓 × 每股现金。港股通 cash 按人民币到账录入。"""
    return hold * float(operation.cash or 0)


def dividend_cash_native(operation: Operation, hold: float, hkd_cny_rate: float) -> float:
    """除权现金影响（原币口径）。港股用当前汇率折回港币。"""
    cash_cny = dividend_cash_cny(operation, hold)
    if not is_hk_code(operation.code):
        return cash_cny
    if hkd_cny_rate <= 0:
        return 0.0
    return cash_cny / hkd_cny_rate
