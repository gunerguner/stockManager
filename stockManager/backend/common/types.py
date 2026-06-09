"""类型定义模块"""
from typing import TypedDict

from ..models import Operation


class RealtimePriceData(TypedDict, total=False):
    """实时价格数据"""
    name: str
    currentPrice: float
    priceOffset: float
    offsetRatio: str
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
    count: int
    fee: float
    sum: float
    comment: str


class StockData(TypedDict):
    """单只股票的计算指标（不含 operationList）"""
    code: str
    name: str
    priceNow: float
    offsetToday: float
    offsetTodayRatio: str
    holdCount: float
    holdCost: float
    overallCost: float
    totalValue: float
    totalValueYesterday: float
    offsetCurrent: float
    offsetCurrentRatio: str
    offsetTotal: float
    moneyWeightedReturn: str
    totalCost: float
    totalOffsetToday: float
    holdingDuration: int
    stockType: str
    isNew: bool


class MarketStatusData(TypedDict, total=False):
    """单市场状态元数据"""
    inTradingHours: bool
    priceUpdatedAt: str | None


class MarketsData(TypedDict, total=False):
    """分市场元数据"""
    cn: MarketStatusData
    hk: MarketStatusData


class OverallData(TypedDict, total=False):
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
    xirrAnnualized: str
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


class WatchResultItem(TypedDict):
    """关注列表 API 返回项"""
    code: str
    name: str
    holding: bool
    priceNow: float | None
    histHigh: float | None  # 近 6 年历史最高价
    pb: float | None
    pe: float | None
    risk: str
    opportunity: str
    leftPoint: float | None
    trendPoint: float | None
    bloodPoint: float | None


class ValuationData(TypedDict):
    """每股估值指标（价格无关）"""
    epsTtm: float | None
    bvps: float | None


OperationDict = dict[str, list[Operation]]
CashFlowList = list[CashFlowData]
OperationDataDict = dict[str, list[OperationData]]
RealtimePriceDict = dict[str, RealtimePriceData]
