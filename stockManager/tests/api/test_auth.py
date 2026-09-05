import json

from backend.common.constants import ResponseStatus


def _post_json(client, path, payload):
    return client.post(path, data=json.dumps(payload), content_type="application/json")


def test_login_rejects_bad_password(api_client, user):
    response = _post_json(
        api_client, "/api/login", {"username": "tester", "password": "wrong"}
    )
    body = response.json()
    assert body["status"] == int(ResponseStatus.ERROR)
    assert "用户名或密码错误" in body["message"]


def test_login_success_then_rejects_duplicate(api_client, user):
    first = _post_json(
        api_client, "/api/login", {"username": "tester", "password": "pass1234"}
    )
    assert first.json()["status"] == int(ResponseStatus.SUCCESS)
    second = _post_json(
        api_client, "/api/login", {"username": "tester", "password": "pass1234"}
    )
    assert second.json()["status"] == int(ResponseStatus.ERROR)
    assert "已登录" in second.json()["message"]


def test_unauthenticated_stocks_is_401(api_client):
    response = api_client.get("/api/stocks")
    assert response.json()["status"] == int(ResponseStatus.UNAUTHORIZED)


def test_current_user_access_levels(api_client, user, staff_user, admin_user):
    api_client.force_login(user)
    assert api_client.get("/api/currentUser").json()["info"]["access"] == ""

    api_client.force_login(staff_user)
    assert api_client.get("/api/currentUser").json()["info"]["access"] == "staff"

    api_client.force_login(admin_user)
    assert api_client.get("/api/currentUser").json()["info"]["access"] == "admin"


def test_logout(auth_client):
    response = auth_client.get("/api/logout")
    assert response.json()["status"] == int(ResponseStatus.SUCCESS)
    denied = auth_client.get("/api/stocks")
    assert denied.json()["status"] == int(ResponseStatus.UNAUTHORIZED)
