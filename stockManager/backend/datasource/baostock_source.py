"""baostock 除权除息数据源"""
from contextlib import contextmanager
from typing import TypedDict

import baostock as bs

from backend.common import logger
from backend.common.utils import safe_float


class DividendRow(TypedDict):
    date: str
    cash: float
    reserve: float
    stock: float


def _to_bs_code(code: str) -> str:
    return f"{code[:2]}.{code[2:]}"


@contextmanager
def baostock_session():
    bs.login()
    try:
        yield
    finally:
        bs.logout()


def per_share_cash(before_tax: str, after_tax: str) -> float:
    """每股现金。税前有值时用税前；ETF 常把金额只写在税后。"""
    before = safe_float(before_tax)
    if before > 0:
        return before
    after = safe_float(after_tax)
    if after > 0:
        return after
    return 0.0


def fetch_dividends(code: str, first_year: int, year_now: int) -> list[DividendRow]:
    """按年拉取除权除息原始行；需在 baostock_session 内调用。"""
    formatted = _to_bs_code(code)
    rows: list[DividendRow] = []
    for year in range(first_year, year_now + 1):
        try:
            result_set = bs.query_dividend_data(
                code=formatted,
                year=str(year),
                yearType="operate",
            )
            while result_set.error_code == "0" and result_set.next():
                data = result_set.get_row_data()
                if len(data) < 14 or not data[6]:
                    continue
                rows.append(
                    DividendRow(
                        date=data[6],
                        cash=per_share_cash(data[9], data[10]),
                        reserve=safe_float(data[11]),
                        stock=safe_float(data[13]),
                    )
                )
        except Exception as e:
            logger.error(f"baostock 分红查询失败 {code} {year}: {e}")
    return rows
