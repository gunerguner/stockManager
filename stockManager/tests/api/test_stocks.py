from datetime import date

from backend.common.constants import ResponseStatus
from backend.models import Operation, StockMeta


def test_stocks_requires_login(api_client):
    response = api_client.get("/api/stocks")
    assert response.json()["status"] == int(ResponseStatus.UNAUTHORIZED)


def test_stocks_returns_calculated_fields(auth_client, user):
    meta = StockMeta.objects.create(code="sh600519", name="贵州茅台", stockType="SH60")
    Operation.objects.create(
        user=user,
        stock_meta=meta,
        date=date(2024, 1, 2),
        operationType=Operation.OperationType.BUY,
        price="10",
        count=100,
        fee="5",
    )
    response = auth_client.get("/api/stocks")
    body = response.json()
    assert body["status"] == int(ResponseStatus.SUCCESS)
    data = body["data"]
    assert "stocks" in data
    assert "overall" in data
    assert len(data["stocks"]) == 1
    stock = data["stocks"][0]
    assert stock["code"] == "sh600519"
    assert stock["holdCount"] == 100
    assert stock["holdCost"] == 10.05
    assert stock["totalValue"] == 1000.0
    overall = data["overall"]
    for key in ("totalValue", "offsetCurrent", "offsetTotal", "offsetToday", "hkdCnyRate"):
        assert key in overall
    assert overall["hkdCnyRate"] == 0.86
