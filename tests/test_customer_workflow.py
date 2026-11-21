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
    # Copy repository data into temporary files so tests do not alter source fixtures.
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
    # Create a customer through the public API for workflow test setup.
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
    # Sign in through the API and return the bearer token for authenticated requests.
    response = client.post(
        "/customers/login",
        json={"email": email, "password": "CorrectHorse123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_registration_authentication_and_customer_ownership(
    isolated_workflow_data: None,
) -> None:
    # Verify registration, authentication, ownership, updates, and deactivation.
    response = client.get("/customers/me/cart")
    assert response.status_code == 401

    customer = register_customer()
    # Password data must be stored securely and excluded from the response.
    assert customer["role"] == "customer"
    assert "password_hash" not in customer
    persisted_customer = repositories.workflow_repository.get_customer(customer["id"])
    assert persisted_customer is not None
    assert persisted_customer["password_hash"] != "CorrectHorse123"
    assert "password" not in persisted_customer
    token = sign_in("CUSTOMER@example.com")
    # Email matching should be case-insensitive and produce an authenticated cart.
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
    # Duplicate normalized emails should be rejected.
    assert duplicate.status_code == 409

    updated = client.patch(
        "/customers/me",
        headers=headers,
        json={"delivery_address": "20 Main Street"},
    )
    assert updated.status_code == 200
    assert updated.json()["delivery_address"] == "20 Main Street"
    # Deactivation should immediately invalidate existing bearer access.
    deactivated = client.delete("/customers/me", headers=headers)
    assert deactivated.status_code == 204
    assert client.get("/customers/me/cart", headers=headers).status_code == 401


def test_authentication_and_cart_client_errors_are_documented_by_status(
    isolated_workflow_data: None,
) -> None:
    register_customer()

    wrong_password = client.post(
        "/customers/login",
        json={"email": "customer@example.com", "password": "WrongPassword123"},
    )
    assert wrong_password.status_code == 401

    invalid_token = client.get(
        "/customers/me/cart",
        headers={"Authorization": "Bearer invalid.token"},
    )
    assert invalid_token.status_code == 401

    headers = {"Authorization": f"Bearer {sign_in()}"}
    missing_item = client.post(
        "/customers/me/cart/items",
        headers=headers,
        json={"item_id": 999999, "quantity": 1},
    )
    assert missing_item.status_code == 404

    invalid_quantity = client.post(
        "/customers/me/cart/items",
        headers=headers,
        json={"item_id": 1111, "quantity": 100},
    )
    assert invalid_quantity.status_code == 422


def test_integration_customer_menu_cart_checkout_preserves_order_snapshot(
    isolated_workflow_data: None,
) -> None:
    # Confirm checkout uses current prices and stores customer and order details.
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

    # Simulate a menu price change after the customer adds the item.
    items = json.loads(repositories.restaurant_repository.item_file.read_text())
    items[0]["price"] = 6.25
    repositories.restaurant_repository.item_file.write_text(json.dumps(items))

    order_response = client.post("/customers/me/checkout", headers=headers)
    # Checkout should use the new price and preserve it in the order.
    assert order_response.status_code == 201
    order = order_response.json()
    assert order["total"] == 12.5
    assert order["items"][0]["unit_price"] == 6.25
    assert order["customer_name"] == "Alex Customer"
    assert order["delivery_address"] == "10 Main Street"

    cart = client.get("/customers/me/cart", headers=headers).json()
    # Successful checkout should clear the cart and persist one order.
    assert cart["items"] == []
    assert cart["total"] == 0
    assert client.get(f"/customers/me/orders/{order['id']}", headers=headers).json() == order
    assert json.loads(repositories.workflow_repository.order_file.read_text())[0]["id"] == order["id"]


def test_regression_unavailable_menu_item_prevents_checkout_and_keeps_cart(
    isolated_workflow_data: None,
) -> None:
    # An unavailable item should block checkout without clearing the cart.
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
    # Adding the now-unavailable item should fail while preserving the original cart.
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
    # Cover cart quantity changes, removal, clearing, and empty checkout rejection.
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

    # Removing the only item should leave an empty cart.
    removed = client.delete("/customers/me/cart/items/1111", headers=headers)
    assert removed.status_code == 200
    assert removed.json()["items"] == []

    client.post(
        "/customers/me/cart/items",
        headers=headers,
        json={"item_id": 1211, "quantity": 1},
    )
    cleared = client.delete("/customers/me/cart", headers=headers)
    # Clearing a cart should also remove its restaurant restriction.
    assert cleared.status_code == 200
    assert cleared.json()["items"] == []
    assert cleared.json()["restaurant_id"] is None

    empty_checkout = client.post("/customers/me/checkout", headers=headers)
    assert empty_checkout.status_code == 409


def test_orders_are_not_visible_to_other_customers_and_openapi_documents_workflow(
    isolated_workflow_data: None,
) -> None:
    # Verify cross-customer isolation and OpenAPI exposure of the checkout workflow.
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
    # Another customer must receive not-found rather than access to the order.
    assert response.status_code == 404

    schema = client.get("/openapi.json").json()
    assert schema["info"]["version"] == "1.0.0"
    assert schema["components"]["securitySchemes"]["BearerAuth"]["type"] == "http"
    assert schema["components"]["securitySchemes"]["BearerAuth"]["scheme"] == "bearer"
    assert "BearerAuth" in str(schema["paths"]["/customers/me/cart"]["get"]["security"])
    assert "/customers/me/checkout" in schema["paths"]
    assert "Revalidates the customer" in schema["paths"]["/customers/me/checkout"]["post"]["description"]
