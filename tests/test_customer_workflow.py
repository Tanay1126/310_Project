import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import repositories
from app.main import app


client = TestClient(app)


@pytest.fixture
def isolated_workflow_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_data = Path(__file__).resolve().parents[1] / "data"
    for repository, field, filename in (
        (repositories.restaurant_repository, "restaurant_file", "restaurants.json"),
        (repositories.restaurant_repository, "menu_file", "menus.json"),
        (repositories.restaurant_repository, "category_file", "categories.json"),
        (repositories.restaurant_repository, "item_file", "items.json"),
        (repositories.workflow_repository, "customer_file", "customers.json"),
        (repositories.workflow_repository, "cart_file", "carts.json"),
        (repositories.workflow_repository, "order_file", "orders.json"),
    ):
        isolated_file = tmp_path / filename
        isolated_file.write_bytes((source_data / filename).read_bytes())
        monkeypatch.setattr(repository, field, isolated_file)


def register_customer(email: str = "customer@example.com") -> dict:
    response = client.post(
        "/customers/",
        json={
            "name": "Alex Customer",
            "email": email,
            "password": "CorrectHorse123",
            "delivery_address": "10 Main Street",
        },
    )
    assert response.status_code == 201
    return response.json()


def sign_in(email: str = "customer@example.com") -> str:
    response = client.post(
        "/customers/login",
        json={"email": email, "password": "CorrectHorse123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_registration_authentication_and_customer_ownership(
    isolated_workflow_data: None,
) -> None:
    response = client.get("/customers/me/cart")
    assert response.status_code == 401

    customer = register_customer()
    assert customer["role"] == "customer"
    assert "password_hash" not in customer
    persisted_customer = repositories.workflow_repository.get_customer(customer["id"])
    assert persisted_customer is not None
    assert persisted_customer["password_hash"] != "CorrectHorse123"
    assert "password" not in persisted_customer
    token = sign_in("CUSTOMER@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    cart = client.get("/customers/me/cart", headers=headers)
    assert cart.status_code == 200
    assert cart.json()["customer_id"] == customer["id"]

    duplicate = client.post(
        "/customers/",
        json={
            "name": "Duplicate",
            "email": "CUSTOMER@example.com",
            "password": "CorrectHorse123",
            "delivery_address": "Another address",
        },
    )
    assert duplicate.status_code == 409

    updated = client.patch(
        "/customers/me",
        headers=headers,
        json={"delivery_address": "20 Main Street"},
    )
    assert updated.status_code == 200
    assert updated.json()["delivery_address"] == "20 Main Street"
    deactivated = client.delete("/customers/me", headers=headers)
    assert deactivated.status_code == 204
    assert client.get("/customers/me/cart", headers=headers).status_code == 401


def test_cart_checkout_recalculates_prices_and_preserves_order_snapshot(
    isolated_workflow_data: None,
) -> None:
    register_customer()
    headers = {"Authorization": f"Bearer {sign_in()}"}

    add_item = client.post(
        "/customers/me/cart/items",
        headers=headers,
        json={"item_id": 1111, "quantity": 2},
    )
    assert add_item.status_code == 200
    assert add_item.json()["total"] == 10.8

    second_restaurant_item = client.post(
        "/customers/me/cart/items",
        headers=headers,
        json={"item_id": 2111, "quantity": 1},
    )
    assert second_restaurant_item.status_code == 409

    items = json.loads(repositories.restaurant_repository.item_file.read_text())
    items[0]["price"] = 6.25
    repositories.restaurant_repository.item_file.write_text(json.dumps(items))

    order_response = client.post("/customers/me/checkout", headers=headers)
    assert order_response.status_code == 201
    order = order_response.json()
    assert order["total"] == 12.5
    assert order["items"][0]["unit_price"] == 6.25
    assert order["customer_name"] == "Alex Customer"
    assert order["delivery_address"] == "10 Main Street"

    cart = client.get("/customers/me/cart", headers=headers).json()
    assert cart["items"] == []
    assert cart["total"] == 0
    assert client.get(f"/customers/me/orders/{order['id']}", headers=headers).json() == order
    assert json.loads(repositories.workflow_repository.order_file.read_text())[0]["id"] == order["id"]


def test_unavailable_menu_item_prevents_checkout_and_keeps_cart(
    isolated_workflow_data: None,
) -> None:
    register_customer()
    headers = {"Authorization": f"Bearer {sign_in()}"}
    client.post(
        "/customers/me/cart/items",
        headers=headers,
        json={"item_id": 1111, "quantity": 1},
    )

    update_response = client.patch(
        "/restaurants/1/menu-items/1111",
        json={"available": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["available"] is False
    add_unavailable = client.post(
        "/customers/me/cart/items",
        headers=headers,
        json={"item_id": 1111, "quantity": 1},
    )
    assert add_unavailable.status_code == 409

    response = client.post("/customers/me/checkout", headers=headers)
    assert response.status_code == 409
    assert client.get("/customers/me/cart", headers=headers).json()["items"][0]["item_id"] == 1111
    assert json.loads(repositories.workflow_repository.order_file.read_text()) == []


def test_cart_quantity_remove_clear_and_empty_checkout(
    isolated_workflow_data: None,
) -> None:
    register_customer()
    headers = {"Authorization": f"Bearer {sign_in()}"}
    client.post(
        "/customers/me/cart/items",
        headers=headers,
        json={"item_id": 1111, "quantity": 1},
    )

    updated = client.patch(
        "/customers/me/cart/items/1111",
        headers=headers,
        json={"quantity": 3},
    )
    assert updated.status_code == 200
    assert updated.json()["total"] == 16.2

    removed = client.delete("/customers/me/cart/items/1111", headers=headers)
    assert removed.status_code == 200
    assert removed.json()["items"] == []

    client.post(
        "/customers/me/cart/items",
        headers=headers,
        json={"item_id": 1211, "quantity": 1},
    )
    cleared = client.delete("/customers/me/cart", headers=headers)
    assert cleared.status_code == 200
    assert cleared.json()["items"] == []
    assert cleared.json()["restaurant_id"] is None

    empty_checkout = client.post("/customers/me/checkout", headers=headers)
    assert empty_checkout.status_code == 409


def test_orders_are_not_visible_to_other_customers_and_openapi_documents_workflow(
    isolated_workflow_data: None,
) -> None:
    register_customer()
    owner_headers = {"Authorization": f"Bearer {sign_in()}"}
    client.post(
        "/customers/me/cart/items",
        headers=owner_headers,
        json={"item_id": 1111, "quantity": 1},
    )
    order = client.post("/customers/me/checkout", headers=owner_headers).json()

    register_customer("other@example.com")
    other_headers = {"Authorization": f"Bearer {sign_in('other@example.com')}"}
    response = client.get(
        f"/customers/me/orders/{order['id']}",
        headers=other_headers,
    )
    assert response.status_code == 404

    schema = client.get("/openapi.json").json()
    assert "/customers/me/checkout" in schema["paths"]
    assert "Revalidates the customer" in schema["paths"]["/customers/me/checkout"]["post"]["description"]
