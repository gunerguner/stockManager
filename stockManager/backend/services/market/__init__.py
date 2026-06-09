"""外部行情数据源适配层（仅负责拉取与标准化，不含缓存编排）"""
from .exchangeRate import fetch_hkd_cny_rate
from .realtimePrice import fetch_prices

__all__ = ['fetch_prices', 'fetch_hkd_cny_rate']
