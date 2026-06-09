"""
股票计算器模块
提供股票指标计算功能，包括单股指标和整体指标计算
"""
from ...common.types import CashFlowList, OperationDict, OverallData, StockData
from ..cache import CacheRepository
from .overall import compute_overall
from .single_stock import build_single_stock


class Calculator:
    """
    股票计算器类

    负责计算股票相关的各项指标，包括：
    - 单股指标：持仓成本、浮动盈亏、累计盈亏等
    - 整体指标：总市值、总盈亏、总资产等
    """

    @classmethod
    def calculate_stock_list(cls, operation_list: OperationDict) -> list[StockData]:
        """
        从原始 operation_list 计算每只股票的指标，返回 stock_list。
        stock_list 中不含 operationList 字段，便于缓存。
        """
        realtime_price_list = CacheRepository.query_stock_prices(list(operation_list))
        stock_meta_dict = CacheRepository.get_stock_meta_dict()
        return [
            build_single_stock(
                code,
                operations,
                realtime_price_list.get(code),
                stock_meta_dict.get(code),
            )
            for code, operations in operation_list.items()
        ]

    @classmethod
    def calculate_overall(
        cls,
        stock_list: list[StockData],
        income_cash: float = 0.0,
        cash_flow_list: CashFlowList | None = None,
        hkd_cny_rate: float = 9.0,
    ) -> OverallData:
        """从 stock_list、income_cash、cash_flow_list 计算整体指标（港股金额按汇率折算为 CNY）"""
        return compute_overall(
            stock_list, income_cash, cash_flow_list or [], hkd_cny_rate
        )
