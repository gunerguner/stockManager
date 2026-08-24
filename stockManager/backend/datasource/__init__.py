"""底层外部数据源适配（仅拉取与标准化，不含缓存编排）"""
from backend.datasource.baostock_source import baostock_session, fetch_dividends
from backend.datasource.baiduValuation import fetch_pe_pb
from backend.datasource.exchangeRate import fetch_hkd_cny_daily_rates, fetch_hkd_cny_rate
from backend.datasource.historicalDaily import fetch_daily_closes
from backend.datasource.historicalHigh import fetch_hist_high
from backend.datasource.realtimePrice import fetch_prices
from backend.datasource.sw_industry import fetch_sw_industry_name

__all__ = [
    "baostock_session",
    "fetch_daily_closes",
    "fetch_dividends",
    "fetch_hist_high",
    "fetch_hkd_cny_daily_rates",
    "fetch_hkd_cny_rate",
    "fetch_pe_pb",
    "fetch_prices",
    "fetch_sw_industry_name",
]
