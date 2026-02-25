"""类型定义模块"""
from typing import TypedDict, List, Dict
from ..models import Operation


class CashFlowData(TypedDict):
    """现金流数据"""
    date: str
    amount: float


class OperationDict(TypedDict):
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
    totalCost: float
    totalOffsetToday: float
    holdingDuration: int
    stockType: str
    isNew: bool


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
    xirrAnnualized: str
    cashFlowList: List[CashFlowData]


class CalculatedResult(TypedDict):
    """计算结果（不含 operationList，用于缓存）"""
    stocks: List[StockData]
    overall: OverallData


OperationList = Dict[str, List[Operation]]
CashFlowList = List[CashFlowData]
OperationListResult = Dict[str, List[OperationDict]]