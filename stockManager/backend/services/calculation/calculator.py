"""
股票计算器模块
提供股票指标计算功能，包括单股指标和整体指标计算（纯计算，无 I/O）
"""
from backend.common.types import CashFlowList, OperationDict, OverallData, RealtimePriceDict, StockData
from backend.models import StockMeta as StockMetaModel
from backend.services.calculation.overall import compute_overall
from backend.services.calculation.single_stock import build_single_stock


class Calculator:
    """股票计算器：单股指标与组合整体指标（调用方负责提供行情与元数据）"""

    @classmethod
    def calculate_stock_list(
        cls,
        operation_list: OperationDict,
        realtime_prices: RealtimePriceDict,
        stock_meta_dict: dict[str, StockMetaModel],
    ) -> list[StockData]:
        """从 operation_list 与外部行情/元数据计算每只股票的指标。"""
        return [
            build_single_stock(
                code,
                operations,
                realtime_prices.get(code),
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
