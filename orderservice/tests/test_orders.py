import pytest
import app as app_module
from store import OrderStore


@pytest.fixture
def client(monkeypatch):
    app_module.app.config["TESTING"] = True
    app_module.store = OrderStore()
    app_module.rate_limit_data.clear()
    monkeypatch.setattr(app_module, "charge_payment", lambda **kwargs: None)
    return app_module.app.test_client()


AUTH = {"Authorization": "Bearer test-token"}


def create_payload():
    return {
        "userId": 1,
        "restaurantId": 10,
        "items": [{"menuItemId": 5, "quantity": 2, "price": 100}],
    }


def create_order(client, key="test-key-1"):
    headers = {"Idempotency-Key": key, **AUTH}
    return client.post("/orders", json=create_payload(), headers=headers)


def test_create_order(client):
    response = create_order(client)
    assert response.status_code == 201
    assert "Location" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_idempotent_repeat_returns_same_order(client):
    response1 = create_order(client, "same-key")
    response2 = create_order(client, "same-key")
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.get_json() == response2.get_json()
    assert response1.headers["Location"] == response2.headers["Location"]


def test_invalid_request_returns_400(client):
    response = client.post(
        "/orders",
        json={"restaurantId": 10, "items": [{"menuItemId": 5, "quantity": 2}]},
        headers={"Idempotency-Key": "invalid-key", **AUTH},
    )
    assert response.status_code == 400


def test_missing_bearer_returns_401(client):
    response = client.post(
        "/orders",
        json=create_payload(),
        headers={"Idempotency-Key": "auth-key"},
    )
    assert response.status_code == 401


def test_unknown_order_returns_404(client):
    response = client.get("/orders/999")
    assert response.status_code == 404


def test_accept_header_returns_406(client):
    response = client.get("/orders", headers={"Accept": "text/html"})
    assert response.status_code == 406


def test_list_filter_sort_and_pagination(client):
    create_order(client, "page-1")
    create_order(client, "page-2")
    response = client.get("/orders?status=pending_payment&sort=-orderId&page=1&limit=1")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_etag_and_if_none_match(client):
    created = create_order(client, "etag-key")
    order_id = created.get_json()["orderId"]
    first = client.get(f"/orders/{order_id}")
    assert first.status_code == 200
    assert "ETag" in first.headers
    assert "Cache-Control" in first.headers
    second = client.get(
        f"/orders/{order_id}",
        headers={"If-None-Match": first.headers["ETag"]},
    )
    assert second.status_code == 304
    assert second.data == b""


def test_patch_requires_matching_if_match(client):
    created = create_order(client, "patch-key")
    order_id = created.get_json()["orderId"]
    current = client.get(f"/orders/{order_id}")
    response = client.patch(
        f"/orders/{order_id}",
        json={"restaurantId": 11},
        headers={**AUTH, "If-Match": '"wrong-etag"'},
    )
    assert current.status_code == 200
    assert response.status_code == 412


def test_options_returns_allow(client):
    response = client.options("/orders")
    assert response.status_code == 204
    assert response.headers["Allow"] == "GET, POST, OPTIONS"


def test_cancellation_returns_422_for_wrong_user(client):
    created = create_order(client, "cancel-key")
    order_id = created.get_json()["orderId"]
    response = client.post(
        f"/orders/{order_id}/cancellation",
        json={"userId": 999},
        headers=AUTH,
    )
    assert response.status_code == 422


def test_delete_returns_204(client):
    created = create_order(client, "delete-key")
    order_id = created.get_json()["orderId"]
    response = client.delete(f"/orders/{order_id}", headers=AUTH)
    assert response.status_code == 204
    assert client.get(f"/orders/{order_id}").status_code == 404


def test_rate_limit_headers_exist(client):
    response = client.get("/orders")
    assert "X-RateLimit-Limit" in response.headers or response.status_code == 429
    assert "X-RateLimit-Remaining" in response.headers or response.status_code == 429