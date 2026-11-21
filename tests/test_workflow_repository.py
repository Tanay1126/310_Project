import json
from pathlib import Path

import pytest

from app.repositories import workflow_repository


@pytest.fixture
def isolated_workflow_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> dict[str, Path]:
    files = {
        "customers": tmp_path / "customers.json",
        "carts": tmp_path / "carts.json",
        "orders": tmp_path / "orders.json",
    }
    for path in files.values():
        path.write_text("[]\n", encoding="utf-8")

    monkeypatch.setattr(workflow_repository, "customer_file", files["customers"])
    monkeypatch.setattr(workflow_repository, "cart_file", files["carts"])
    monkeypatch.setattr(workflow_repository, "order_file", files["orders"])
    return files


def test_repository_assigns_stable_ids_and_persists_customer_records(
    isolated_workflow_repository: dict[str, Path],
) -> None:
    first = workflow_repository.create_customer(
        {"name": "First", "email": "first@example.com", "active": True}
    )
    second = workflow_repository.create_customer(
        {"name": "Second", "email": "second@example.com", "active": True}
    )

    assert first["id"] == 1
    assert second["id"] == 2
    assert workflow_repository.get_customer(1) == first
    assert workflow_repository.get_customer_by_email("second@example.com") == second

    updated = workflow_repository.update_customer(1, {"delivery_address": "Main Street"})
    assert updated is not None
    assert workflow_repository.get_customer(1)["delivery_address"] == "Main Street"
    assert workflow_repository.get_customer(999) is None

    records = json.loads(isolated_workflow_repository["customers"].read_text())
    assert [record["id"] for record in records] == [1, 2]


def test_repository_merges_cart_updates_and_preserves_cart_id(
    isolated_workflow_repository: dict[str, Path],
) -> None:
    created = workflow_repository.save_cart(
        {"customer_id": 7, "restaurant_id": 1, "items": [{"item_id": 1111, "quantity": 1}]}
    )
    updated = workflow_repository.save_cart(
        {"customer_id": 7, "restaurant_id": 1, "items": [{"item_id": 1111, "quantity": 3}]}
    )

    assert created["id"] == 1
    assert updated["id"] == 1
    assert updated["items"][0]["quantity"] == 3
    assert workflow_repository.get_cart(7) == updated
    assert workflow_repository.get_cart(999) is None

    records = json.loads(isolated_workflow_repository["carts"].read_text())
    assert len(records) == 1
    assert records[0]["id"] == 1


def test_repository_persists_orders_with_stable_ids_and_customer_lookup(
    isolated_workflow_repository: dict[str, Path],
) -> None:
    first = workflow_repository.create_order(
        {"customer_id": 7, "restaurant_id": 1, "items": [], "total": 5.0}
    )
    second = workflow_repository.create_order(
        {"customer_id": 8, "restaurant_id": 2, "items": [], "total": 8.0}
    )

    assert first["id"] == 1
    assert second["id"] == 2
    assert workflow_repository.get_order(1) == first
    assert workflow_repository.get_customer_orders(7) == [first]
    assert workflow_repository.get_customer_orders(8) == [second]

    records = json.loads(isolated_workflow_repository["orders"].read_text())
    assert [record["id"] for record in records] == [1, 2]
