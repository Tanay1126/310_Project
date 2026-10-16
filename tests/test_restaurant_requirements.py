import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import repositories
from app.main import app

client = TestClient(app)


@pytest.fixture
def isolated_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source_data = Path(__file__).resolve().parents[1] / "data"
    restaurant_path = tmp_path / "restaurants.json"
    item_path = tmp_path / "items.json"
    restaurant_path.write_bytes((source_data / "restaurants.json").read_bytes())
    item_path.write_bytes((source_data / "items.json").read_bytes())
    monkeypatch.setattr(repositories.restaurant_repository, "restaurant_file", restaurant_path)
    monkeypatch.setattr(repositories.restaurant_repository, "item_file", item_path)


def test_restaurant_search_and_filters(isolated_data: None) -> None:
    response = client.get("/restaurants/", params={"q": "sushi", "cuisine": "japan"})
    assert response.status_code == 200
    assert [restaurant["id"] for restaurant in response.json()] == [1]

    response = client.get("/restaurants/", params={"min_rating": 4.5})
    assert response.status_code == 200
    assert [restaurant["id"] for restaurant in response.json()] == [1, 2]


def test_read_menu_and_its_items(isolated_data: None) -> None:
    response = client.get("/restaurants/1/menus/11")
    assert response.status_code == 200
    assert response.json()["categories"][0]["items"][0]["name"] == "Mochi"

    response = client.get("/restaurants/1/menus/11/items")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [1111]


def test_create_and_update_restaurant(isolated_data: None) -> None:
    response = client.post(
        "/restaurants/",
        json={"name": "New Bistro", "cuisine": "French", "rating": 4.8},
    )
    assert response.status_code == 201
    restaurant_id = response.json()["id"]

    response = client.patch(
        f"/restaurants/{restaurant_id}",
        json={"description": "A neighborhood restaurant"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "A neighborhood restaurant"
    assert response.json()["name"] == "New Bistro"

    records = json.loads(repositories.restaurant_repository.restaurant_file.read_text())
    assert records[-1]["id"] == restaurant_id


def test_create_read_and_update_menu_item(isolated_data: None) -> None:
    response = client.post(
        "/restaurants/1/menu-items",
        json={"category_id": 111, "name": "Dorayaki", "price": 4.25},
    )
    assert response.status_code == 201
    item_id = response.json()["id"]

    response = client.get(f"/restaurants/1/menu-items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Dorayaki"

    response = client.patch(
        f"/restaurants/1/menu-items/{item_id}",
        json={"price": 4.5},
    )
    assert response.status_code == 200
    assert response.json()["price"] == 4.5

    response = client.post(
        "/restaurants/1/menu-items",
        json={"category_id": 999999, "name": "Orphan", "price": 1.0},
    )
    assert response.status_code == 404
