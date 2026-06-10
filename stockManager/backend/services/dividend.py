"""
分红服务模块
提供股票分红数据查询和处理功能
"""
import datetime

from django.contrib.auth.models import User

from ..common import logger
from ..common.constants import OperationType
from ..common.types import OperationDict, DividendUpdateData
from ..common.utils import operation_sort_key
from ..models import Operation
from .cache import CacheRepository
from .calculation import StockHold
from .market import baostock_session, fetch_dividends


class Dividend:
    """分红服务类，负责处理股票分红相关操作（纯工具类，无状态）"""

    @classmethod
    def generate_dividend(cls, user: User, operation_list: OperationDict) -> list[DividendUpdateData]:
        """为持有的股票生成分红数据"""
        holding_stocks = StockHold.get_holding_stocks(operation_list)
        cn_holding = [code for code in holding_stocks if not code.lower().startswith("hk")]
        if not cn_holding:
            return []

        updated_codes: list[DividendUpdateData] = []
        stock_meta_dict = CacheRepository.get_stock_meta_dict()

        with baostock_session():
            for code in cn_holding:
                operations = operation_list[code]
                updated_code = cls._generate_dividend_single(user, code, operations)
                if updated_code:
                    stock_meta = stock_meta_dict.get(updated_code)
                    updated_codes.append({
                        "code": updated_code,
                        "name": stock_meta.name if stock_meta and stock_meta.name else updated_code,
                    })

        return updated_codes

    @classmethod
    def _first_query_year(
        cls,
        operations: list[Operation],
        exist_dv_operations: list[Operation],
    ) -> int:
        first_year = min(op.date.year for op in operations)
        if exist_dv_operations:
            max_div_year = max(op.date.year for op in exist_dv_operations)
            # 从最后一次有记录的分红年份起扫（含该年），配合 date_set 去重
            return max(first_year, max_div_year)
        return first_year

    @classmethod
    def _generate_dividend_single(cls, user: User, code: str, operations: list[Operation]) -> str:
        """生成个股除权除息信息"""
        if not operations:
            return ""

        try:
            today = datetime.date.today()
            three_days_later = today + datetime.timedelta(days=3)
            update_count = 0

            exist_dv_operations = [op for op in operations if op.operationType == OperationType.DIVIDEND]
            date_set = {str(op.date) for op in exist_dv_operations}

            year_now = today.year
            first_query_year = cls._first_query_year(operations, exist_dv_operations)
            sorted_operations = sorted(operations, key=operation_sort_key)

            for row in fetch_dividends(code, first_query_year, year_now):
                dividend_date_str = row["date"]
                try:
                    dividend_date = datetime.datetime.strptime(
                        dividend_date_str, "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError) as e:
                    logger.warning(f"分红日期格式解析失败: {dividend_date_str}, 错误: {e}")
                    continue

                if dividend_date > three_days_later:
                    continue
                if dividend_date_str in date_set:
                    continue

                hold_count_at_date = StockHold.calculate_hold_count_at_date(
                    sorted_operations, dividend_date
                )
                if hold_count_at_date <= 0:
                    continue

                Operation.objects.create(
                    user=user,
                    date=dividend_date,
                    code=code,
                    operationType=OperationType.DIVIDEND,
                    cash=row["cash"],
                    reserve=row["reserve"],
                    stock=row["stock"],
                    count=hold_count_at_date,
                )
                update_count += 1
                date_set.add(dividend_date_str)

            return code if update_count > 0 else ""

        except Exception as e:
            logger.error(f"生成股票 {code} 分红信息失败: {e}")
            return ""
