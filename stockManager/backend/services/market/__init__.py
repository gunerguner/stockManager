"""外部行情数据源适配层（仅负责拉取与标准化，不含缓存编排）"""
from .baostock_source import (
    baostock_session,
    fetch_cn_hist_highs,
    fetch_cn_valuation,
    fetch_dividends,
)
from .baiduValuation import fetch_pe_pb
from .exchangeRate import fetch_hkd_cny_rate
from .historicalHigh import fetch_hk_hist_high
from .realtimePrice import fetch_prices

__all__ = [
    "baostock_session",
    "fetch_cn_hist_highs",
    "fetch_cn_valuation",
    "fetch_dividends",
    "fetch_hk_hist_high",
    "fetch_hkd_cny_rate",
    "fetch_pe_pb",
    "fetch_prices",
]
