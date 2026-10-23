from datetime import date

import pytest

from backend.common.constants import OperationType
from backend.datasource.baostock_source import per_share_cash
from backend.models import Operation, StockMeta
from backend.services.app import dividend as dividend_mod


def test_per_share_cash_prefers_before_tax_and_falls_back_to_after_tax():
    assert per_share_cash("0.2", "0.18或0.2") == 0.2
    assert per_share_cash("0", "0.014") == 0.014
    assert per_share_cash("", "0.014") == 0.014
    assert per_share_cash("0", "") == 0.0


@pytest.mark.django_db
def test_skips_blank_and_nearby_dividend(user, monkeypatch):
    meta = StockMeta.objects.create(code="sh588080", name="科创50ETF", stockType="FUNDIN")
    buy = Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=date(2025, 1, 2),
        operationType=OperationType.BUY,
        count=1000,
    )
    existing = Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=date(2025, 10, 21),
        operationType=OperationType.DIVIDEND,
        cash="0.014",
        count=1000,
    )
    monkeypatch.setattr(
        dividend_mod,
        "fetch_dividends",
        lambda code, first_year, year_now: [
            {"date": "2025-10-17", "cash": 0.0, "reserve": 0.0, "stock": 0.0},
            {"date": "2025-10-17", "cash": 0.014, "reserve": 0.0, "stock": 0.0},
        ],
    )

    assert dividend_mod.Dividend._generate_dividend_single(user, "sh588080", [buy, existing]) == ""
    assert Operation.objects.filter(stock_meta=meta, operationType=OperationType.DIVIDEND).count() == 1


@pytest.mark.django_db
def test_inserts_ex_date_cash_when_no_nearby_record(user, monkeypatch):
    meta = StockMeta.objects.create(code="sh588080", name="科创50ETF", stockType="FUNDIN")
    buy = Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=date(2025, 1, 2),
        operationType=OperationType.BUY,
        count=1000,
    )
    monkeypatch.setattr(
        dividend_mod,
        "fetch_dividends",
        lambda code, first_year, year_now: [
            {"date": "2025-10-17", "cash": 0.0, "reserve": 0.0, "stock": 0.0},
            {"date": "2025-10-17", "cash": 0.014, "reserve": 0.0, "stock": 0.0},
        ],
    )

    assert dividend_mod.Dividend._generate_dividend_single(user, "sh588080", [buy]) == "sh588080"
    created = Operation.objects.get(stock_meta=meta, operationType=OperationType.DIVIDEND)
    assert created.date == date(2025, 10, 17)
    assert float(created.cash) == pytest.approx(0.014)
