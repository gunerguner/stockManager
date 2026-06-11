"""外部行情数据源适配层（仅负责拉取与标准化，不含缓存编排）"""
from backend.services.market.baostock_source import baostock_session, fetch_dividends
from backend.services.market.baiduValuation import fetch_pe_pb
from backend.services.market.exchangeRate import fetch_hkd_cny_rate
from backend.services.market.historicalHigh import fetch_cn_hist_high, fetch_hk_hist_high
from backend.services.market.realtimePrice import fetch_prices

__all__ = [
    "baostock_session",
    "fetch_cn_hist_high",
    "fetch_dividends",
    "fetch_hk_hist_high",
    "fetch_hkd_cny_rate",
    "fetch_pe_pb",
    "fetch_prices",
]
