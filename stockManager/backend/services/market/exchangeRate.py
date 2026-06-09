"""HKD/CNY 即期汇率外部数据源（akshare / 中国外汇交易中心）"""
import akshare as ak


def fetch_hkd_cny_rate() -> float:
    """从 akshare 获取 HKD/CNY 即期汇率（1 HKD = X CNY）"""
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
