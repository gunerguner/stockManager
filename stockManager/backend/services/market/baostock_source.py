"""baostock 统一数据源（A 股估值、历史高、除权除息）"""
import datetime
from contextlib import contextmanager
from typing import TypedDict

import baostock as bs

from ...common import logger
from ...common.utils import safe_float

_MONTHS = 72  # 6 年


class DividendRow(TypedDict):
    date: str
    cash: float
    reserve: float
    stock: float


class CnValuationRow(TypedDict):
    peTTM: float | None
    pbMRQ: float | None
    close: float | None


def _to_bs_code(code: str) -> str:
    return f"{code[:2]}.{code[2:]}"


@contextmanager
def baostock_session():
    bs.login()
    try:
        yield
    finally:
        bs.logout()


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
                rows.append(
                    DividendRow(
                        date=data[6],
                        cash=safe_float(data[9]),
                        reserve=safe_float(data[11]),
                        stock=safe_float(data[13]),
                    )
                )
        except Exception as e:
            logger.error(f"baostock 分红查询失败 {code} {year}: {e}")
    return rows


def fetch_cn_valuation(codes: list[str]) -> dict[str, CnValuationRow]:
    """批量获取 A 股最新 peTTM / pbMRQ / close。"""
    if not codes:
        return {}

    end = datetime.date.today()
    start = end - datetime.timedelta(days=30)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    empty: CnValuationRow = {"peTTM": None, "pbMRQ": None, "close": None}
    result: dict[str, CnValuationRow] = {}

    with baostock_session():
        for code in codes:
            try:
                rs = bs.query_history_k_data_plus(
                    _to_bs_code(code),
                    "date,close,peTTM,pbMRQ",
                    start_date=start_str,
                    end_date=end_str,
                    frequency="d",
                    adjustflag="3",
                )
                if rs.error_code != "0":
                    logger.error(f"baostock 估值失败 {code}: {rs.error_msg}")
                    result[code] = empty
                    continue

                last_close: float | None = None
                last_pe: float | None = None
                last_pb: float | None = None
                while rs.next():
                    row = rs.get_row_data()
                    close_raw, pe_raw, pb_raw = row[1], row[2], row[3]
                    if close_raw:
                        last_close = safe_float(close_raw)
                    if pe_raw:
                        last_pe = safe_float(pe_raw)
                    if pb_raw:
                        last_pb = safe_float(pb_raw)

                result[code] = CnValuationRow(
                    peTTM=last_pe,
                    pbMRQ=last_pb,
                    close=last_close,
                )
            except Exception as e:
                logger.error(f"baostock 估值异常 {code}: {e}")
                result[code] = empty

    return result


def fetch_cn_hist_highs(codes: list[str]) -> dict[str, float | None]:
    """批量获取 A 股近 6 年周线前复权最高价。"""
    if not codes:
        return {}

    end = datetime.date.today()
    start = end - datetime.timedelta(days=_MONTHS * 31)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    result: dict[str, float | None] = {}

    with baostock_session():
        for code in codes:
            try:
                rs = bs.query_history_k_data_plus(
                    _to_bs_code(code),
                    "date,high",
                    start_date=start_str,
                    end_date=end_str,
                    frequency="w",
                    adjustflag="2",
                )
                if rs.error_code != "0":
                    logger.error(f"baostock 历史高失败 {code}: {rs.error_msg}")
                    result[code] = None
                    continue

                highs: list[float] = []
                while rs.next():
                    row = rs.get_row_data()
                    high_raw = row[1]
                    if high_raw:
                        highs.append(safe_float(high_raw))
                result[code] = max(highs) if highs else None
            except Exception as e:
                logger.error(f"baostock 历史高异常 {code}: {e}")
                result[code] = None

    return result
