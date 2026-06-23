"""类型定义模块"""
from typing import TypedDict

from backend.models import Operation


class RealtimePriceData(TypedDict):
    """实时价格数据"""
    name: str
    currentPrice: float
    priceOffset: float
    offsetRatio: float  # 原始比率，如 0.0123 表示 1.23%
    yesterdayClose: float
    yearHigh: float | None


class CashFlowData(TypedDict):
    """现金流数据"""
    date: str
    amount: float


class OperationData(TypedDict):
    """单个操作记录的字典格式（API返回格式）"""
    date: str
    type: str
    price: float
    count: int  # 单笔成交股数，整股
    fee: float
    sum: float
    comment: str


class StockData(TypedDict):
    """单只股票的计算指标（不含 operationList）"""
    code: str
    name: str
    priceNow: float
    offsetToday: float
    offsetTodayRatio: float  # 原始比率
    holdCount: float  # 持仓份额，基金等可为小数
    holdCost: float
    overallCost: float
    totalValue: float
    totalValueYesterday: float
    offsetCurrent: float
    offsetCurrentRatio: float  # 原始比率
    offsetTotal: float
    moneyWeightedReturn: float  # 原始比率
    totalCost: float
    totalOffsetToday: float
    holdingDuration: int
    stockType: str
    isNew: bool


class MarketStatusData(TypedDict):
    """单市场状态元数据"""
    inTradingHours: bool
    priceUpdatedAt: str | None


class MarketsData(TypedDict, total=False):
    """分市场元数据"""
    cn: MarketStatusData
    hk: MarketStatusData


class OverallData(TypedDict):
    """整体指标"""
    offsetCurrent: float
    offsetTotal: float
    totalValue: float
    offsetToday: float
    totalCash: float
    totalAsset: float
    totalCost: float
    incomeCash: float
    originCash: float
    xirrAnnualized: float  # 原始比率
    cashFlowList: list[CashFlowData]
    hkdCnyRate: float


class CalculatedResult(TypedDict):
    """计算结果（不含 operationList，用于缓存）"""
    stocks: list[StockData]
    overall: OverallData
    markets: MarketsData


class DividendUpdateData(TypedDict):
    """除权更新项"""
    code: str
    name: str


class WatchItemDict(TypedDict):
    """关注列表原始项（缓存/DB）"""
    code: str
    risk: str
    opportunity: str
    leftPoint: float | None
    trendPoint: float | None
    bloodPoint: float | None


class WatchResultItem(TypedDict, total=False):
    """关注列表 API 返回项"""
    code: str
    name: str
    holding: bool
    priceNow: float | None
    offsetToday: float
    offsetTodayRatio: float  # 原始比率
    histHigh: float | None  # 近 6 年历史最高价
    pb: float | None
    pe: float | None
    risk: str
    opportunity: str
    leftPoint: float | None
    trendPoint: float | None
    bloodPoint: float | None
    offsetTotal: float  # 累计盈亏（仅持仓股票），用最新现价即时计算，用于 HoldingStatus 图标颜色


class ValuationData(TypedDict):
    """每股估值指标（价格无关）"""
    epsTtm: float | None
    bvps: float | None


OperationDict = dict[str, list[Operation]]
CashFlowList = list[CashFlowData]
OperationDataDict = dict[str, list[OperationData]]
RealtimePriceDict = dict[str, RealtimePriceData]
