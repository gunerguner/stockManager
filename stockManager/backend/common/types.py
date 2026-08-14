"""类型定义模块"""
from datetime import date
from typing import TypedDict

from backend.models import Operation


class RealtimePriceData(TypedDict):
    """实时价格数据"""
    name: str
    currentPrice: float
    priceOffset: float
    offsetRatio: float  # 原始比率，如 0.0123 表示 1.23%
    yesterdayClose: float


class CashFlowData(TypedDict):
    """现金流数据"""
    date: str
    amount: float


class OperationData(TypedDict):
    """单个操作记录的字典格式（API返回格式，原始字段）"""
    date: str
    type: str
    price: float
    count: int  # 单笔成交股数，整股
    fee: float
    amount: float | None  # 港股通人民币成交额；非港股为空
    comment: str
    cash: float
    stock: float
    reserve: float


class StockData(TypedDict):
    """单只股票的计算指标（不含 operationList）

    金额类主字段统一为人民币（CNY）；港股价格/成本仍为港币。
    港币 tooltip 由前端用 priceNow/holdCost/overallCost/holdCount 推导。
    """
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
    hidden: bool


class WatchResultItem(TypedDict, total=False):
    """关注列表 API 返回项"""
    code: str
    name: str
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
    hidden: bool


class ValuationData(TypedDict):
    """每股估值指标（价格无关）"""
    epsTtm: float | None
    bvps: float | None


class NavPointData(TypedDict):
    """净值序列点"""
    date: str
    nav: float
    navDisplay: float


class NavMaxNavMarker(TypedDict):
    """区间最高净值锚点"""
    date: str
    display: float


class NavDrawdownPeriod(TypedDict):
    """最大回撤区间（峰 / 谷 / 收复或未收复终点）"""
    peakDate: str
    troughDate: str
    endDate: str
    recovered: bool
    recoverDays: int | None


class NavMetricsData(TypedDict):
    """净值区间指标（原始比率）+ 图表标注锚点"""
    annualizedReturn: float
    sharpeRatio: float
    maxDrawdown: float
    calmarRatio: float
    maxNav: NavMaxNavMarker | None
    drawdown: NavDrawdownPeriod | None


class NavMetricsByRange(TypedDict):
    all: NavMetricsData
    ytd: NavMetricsData
    oneYear: NavMetricsData


class NavAnalysisResult(TypedDict):
    """净值分析 API / Redis 缓存结构"""
    points: list[NavPointData]
    metrics: NavMetricsByRange
    incomeCash: float
    originCash: float
    lastDate: str | None
    updatedAt: str | None


OperationDict = dict[str, list[Operation]]
CashFlowList = list[CashFlowData]
OperationDataDict = dict[str, list[OperationData]]
RealtimePriceDict = dict[str, RealtimePriceData]

# 日频行情 / 净值持仓窗口
DateRange = tuple[date, date]
DateRangeList = list[DateRange]
HoldingWindows = dict[str, DateRangeList]  # code -> [(start, end), ...]
DailyCloseSeries = dict[date, float]  # date -> close
DailyCloseByCode = dict[str, DailyCloseSeries]  # code -> series
DailyFxSeries = dict[date, float]  # date -> HKD/CNY
