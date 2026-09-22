import pytest

import app as app_module
from store import OrderStore


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True

    # Fresh store for every test
    app_module.store = OrderStore()

    return app_module.app.test_client()


def test_create_order(client):

    response = client.post(
        "/orders",
        json={
            "userId": 1,
            "restaurantId": 10,
            "items": [
                {
                    "menuItemId": 5,
                    "quantity": 2,
                    "price": 100
                }
            ]
        },
        headers={
            "Idempotency-Key": "test-key-1"
        }
    )

    assert response.status_code == 201
    assert "Location" in response.headers


def test_idempotent_repeat_returns_same_order(client):

    order_data = {
        "userId": 1,
        "restaurantId": 10,
        "items": [
            {
                "menuItemId": 5,
                "quantity": 2,
                "price": 100
            }
        ]
    }

    headers = {
        "Idempotency-Key": "same-key"
    }

    # First request
    response1 = client.post(
        "/orders",
        json=order_data,
        headers=headers
    )

    # Second request with same key
    response2 = client.post(
        "/orders",
        json=order_data,
        headers=headers
    )

    assert response1.status_code == 201
    assert response2.status_code == 201

    # Both responses should contain the same order
    assert response1.get_json() == response2.get_json()

    # Same Location should be returned
    assert response1.headers["Location"] == response2.headers["Location"]


def test_invalid_request_returns_4xx(client):

    response = client.post(
        "/orders",
        json={
            "restaurantId": 10,
            "items": [
                {
                    "menuItemId": 5,
                    "quantity": 2
                }
            ]
        },
        headers={
            "Idempotency-Key": "invalid-key"
        }
    )

    assert response.status_code == 400


def test_unknown_order_returns_404(client):

    response = client.get("/orders/999")

    assert response.status_code == 404