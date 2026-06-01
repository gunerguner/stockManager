"""HKD/CNY 即期汇率服务"""
from typing import Iterable

import requests
from django.core.cache import cache

from ..common import logger
from ..common.market import Market, markets_in_codes
from ..common.tradingCalendar import TradingCalendar
from .cache import keys


class ExchangeRate:
    """港股通汇总用 HKD/CNY 汇率（1 HKD = X CNY）"""

    @classmethod
    def get_hkd_cny_rate(cls, user_codes: Iterable[str]) -> float:
        markets = markets_in_codes(user_codes)
        if Market.HK not in markets:
            return 1.0

        in_trading = any(
            TradingCalendar.is_current_time_in_trading_hours(m) for m in markets
        )
        if in_trading:
            rate = cls._fetch_from_api()
            cache.set(keys.KEY_FX_HKD_CNY, rate, keys.TTL_FX)
            return rate

        cached = cache.get(keys.KEY_FX_HKD_CNY)
        if cached is not None:
            return float(cached)

        rate = cls._fetch_from_api()
        cache.set(keys.KEY_FX_HKD_CNY, rate, keys.TTL_FX)
        return rate

    @classmethod
    def _fetch_from_api(cls) -> float:
        try:
            return cls._fetch_akshare()
        except Exception as e:
            logger.warning(f"akshare 汇率获取失败，尝试新浪: {e}")
        return cls._fetch_sina()

    @classmethod
    def _fetch_akshare(cls) -> float:
        import akshare as ak

        df = ak.fx_spot_quote()
        pair_col = "货币对" if "货币对" in df.columns else df.columns[0]
        buy_col = "买报价" if "买报价" in df.columns else df.columns[1]
        row = df[df[pair_col].astype(str).str.upper() == "HKD/CNY"]
        if row.empty:
            raise ValueError("akshare 未返回 HKD/CNY")
        rate = float(row.iloc[0][buy_col])
        if rate <= 0:
            raise ValueError(f"无效汇率: {rate}")
        return rate

    @classmethod
    def _fetch_sina(cls) -> float:
        resp = requests.get(
            "https://hq.sinajs.cn/list=fx_shkdcny",
            headers={"Referer": "https://finance.sina.com.cn"},
            timeout=10,
        )
        resp.raise_for_status()
        text = resp.text
        # var hq_str_fx_shkdcny="...,0.8688,...";
        if '="' not in text:
            raise ValueError("新浪汇率响应格式异常")
        payload = text.split('="')[1].rstrip('";')
        parts = payload.split(",")
        for part in reversed(parts):
            try:
                rate = float(part)
                if 0 < rate < 2:
                    return rate
            except ValueError:
                continue
        raise ValueError("新浪汇率解析失败")
