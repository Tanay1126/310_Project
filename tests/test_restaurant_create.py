import json

from fastapi.testclient import TestClient

from app.api.routes import restaurants as restaurant_routes
from app.main import app
from app.repositories.restaurant_repository import create_restaurant as save_restaurant


client = TestClient(app)


def test_homepage_serves_frontend():
    response = client.get("/")

    assert response.status_code == 200
    assert "Restaurant Directory" in response.text


def test_create_restaurant_persists_and_assigns_id(tmp_path):
    data_file = tmp_path / "restaurants.json"
    data_file.write_text(
        json.dumps([{"id": 3, "name": "Existing Restaurant"}]),
        encoding="utf-8",
    )

    created = save_restaurant(
        {"name": "New Restaurant", "cuisine": "Thai"},
        data_file=data_file,
    )

    assert created == {"id": 4, "name": "New Restaurant", "cuisine": "Thai"}
    assert json.loads(data_file.read_text(encoding="utf-8")) == [
        {"id": 3, "name": "Existing Restaurant"},
        {"id": 4, "name": "New Restaurant", "cuisine": "Thai"},
    ]


def test_create_restaurant_endpoint_returns_created_restaurant(monkeypatch):
    monkeypatch.setattr(
        restaurant_routes,
        "create_restaurant",
        lambda restaurant: {
            "id": 4,
            **restaurant.model_dump(exclude_none=True),
        },
    )

    response = client.post(
        "/restaurants/",
        json={
            "name": "New Restaurant",
            "cuisine": "Thai",
            "description": "Fresh noodles",
            "rating": 4.6,
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 4,
        "name": "New Restaurant",
        "cuisine": "Thai",
        "description": "Fresh noodles",
        "rating": 4.6,
    }


def test_create_restaurant_endpoint_validates_rating():
    response = client.post(
        "/restaurants/",
        json={"name": "New Restaurant", "rating": 6},
    )

    assert response.status_code == 422


def test_create_restaurant_endpoint_rejects_blank_name():
    response = client.post("/restaurants/", json={"name": "   "})

    assert response.status_code == 422
