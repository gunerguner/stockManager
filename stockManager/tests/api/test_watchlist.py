from backend.common.constants import ResponseStatus
from backend.models import StockMeta, WatchItem


def test_watchlist_empty(auth_client):
    response = auth_client.get("/api/watchlist")
    body = response.json()
    assert body["status"] == int(ResponseStatus.SUCCESS)
    assert body["data"] == []


def test_watchlist_hidden_roundtrip(auth_client, user):
    meta = StockMeta.objects.create(code="sz000001", name="平安银行", stockType="SZ00")
    WatchItem.objects.create(user=user, stock_meta=meta, hidden=False)

    listed = auth_client.get("/api/watchlist").json()["data"]
    assert len(listed) == 1
    assert listed[0]["code"] == "sz000001"
    assert listed[0]["hidden"] is False

    update = auth_client.post(
        "/api/watchlist/hidden",
        data='{"code": "sz000001", "hidden": true}',
        content_type="application/json",
    )
    assert update.json()["status"] == int(ResponseStatus.SUCCESS)

    after = auth_client.get("/api/watchlist").json()["data"]
    assert after[0]["hidden"] is True


def test_watchlist_hidden_missing_item(auth_client):
    response = auth_client.post(
        "/api/watchlist/hidden",
        data='{"code": "sh600519", "hidden": true}',
        content_type="application/json",
    )
    assert response.json()["status"] == int(ResponseStatus.ERROR)
    assert "关注项不存在" in response.json()["message"]
