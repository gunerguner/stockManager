"""HKD/CNY 即期汇率外部数据源（新浪外汇）"""
import re

from backend.services.market.http_client import get_text

_SINA_FX_URL = "https://hq.sinajs.cn/list=fx_shkdcny"
_SINA_REFERER = "https://finance.sina.com.cn/"


def fetch_hkd_cny_rate() -> float:
    """从新浪外汇获取 HKD/CNY 即期汇率（1 HKD = X CNY）"""
    text = get_text(
        _SINA_FX_URL,
        headers={"Referer": _SINA_REFERER},
    )
    match = re.search(r'="([^"]+)"', text)
    if not match:
        raise ValueError("sina 外汇响应格式异常")
    parts = match.group(1).split(",")
    if len(parts) < 2:
        raise ValueError(f"sina 外汇字段不足: {parts}")
    rate = float(parts[1])
    if rate <= 0:
        raise ValueError(f"无效汇率: {rate}")
    return rate
