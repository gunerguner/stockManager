"""
分红用例：从外部源拉取除权除息并写入 Operation
"""
import datetime

from django.contrib.auth.models import User

from backend.common import logger
from backend.common.constants import OperationType
from backend.common.money import quantize_cash
from backend.common.types import OperationDict, DividendUpdateData
from backend.common.utils import operation_sort_key
from backend.datasource import baostock_session, fetch_dividends
from backend.datasource.baostock_source import DividendRow
from backend.models import Operation, StockMeta
from backend.services.cache import CacheRepository
from backend.services.calculation import StockHold

# 除息日与手工入账日（常落在发放日附近）允许的间隔
_NEARBY_DIVIDEND_DAYS = 4


class Dividend:
    """分红服务类，负责处理股票分红相关操作"""

    @classmethod
    def generate_dividend(cls, user: User, operation_list: OperationDict) -> list[DividendUpdateData]:
        """为持有的股票生成分红数据"""
        holding_stocks = StockHold.get_holding_stocks(operation_list)
        if not (
            cn_holding := [
                code for code in holding_stocks if not code.lower().startswith("hk")
            ]
        ):
            return []

        updated_codes: list[DividendUpdateData] = []
        stock_meta_dict = CacheRepository.get_stock_meta_dict()

        with baostock_session():
            for code in cn_holding:
                operations = operation_list[code]
                if updated_code := cls._generate_dividend_single(user, code, operations):
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
            exist_dates = {op.date for op in exist_dv_operations}

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
                if dividend_date in exist_dates:
                    continue
                if _is_blank_dividend(row):
                    continue
                if _has_nearby_dividend(dividend_date, exist_dates):
                    continue

                hold_count_at_date = StockHold.calculate_hold_count_at_date(
                    sorted_operations, dividend_date
                )
                if hold_count_at_date <= 0:
                    continue

                Operation.objects.create(
                    user=user,
                    date=dividend_date,
                    stock_meta=StockMeta.objects.get(code=code),
                    operationType=OperationType.DIVIDEND,
                    cash=quantize_cash(row["cash"]),
                    reserve=row["reserve"],
                    stock=row["stock"],
                    count=hold_count_at_date,
                )
                update_count += 1
                exist_dates.add(dividend_date)

            return code if update_count > 0 else ""

        except Exception as e:
            logger.error(f"生成股票 {code} 分红信息失败: {e}")
            return ""


def _is_blank_dividend(row: DividendRow) -> bool:
    """现金、送股、转增都没有时，不生成记录。"""
    return row["cash"] <= 0 and row["stock"] <= 0 and row["reserve"] <= 0


def _has_nearby_dividend(dividend_date: datetime.date, exist_dates: set[datetime.date]) -> bool:
    """同一事件常被记在除息日或发放日，间隔数天内视为已入账。"""
    return any(
        abs((dividend_date - existing).days) <= _NEARBY_DIVIDEND_DAYS
        for existing in exist_dates
    )
