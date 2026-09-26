from fastapi.testclient import TestClient
import pytest
from app.repositories.restaurant_repository import read_restaurants
from app.main import app

client = TestClient(app)


def test_read_restaurant():
    response = client.get("/restaurants/")
    assert response.status_code == 200

def test_read_item_id():
    response = client.get("/restaurants/1")
    assert response.status_code == 200

def test_read_item_id_not_found():
    response = client.get("/restaurants/999")
    assert response.status_code == 404

def test_get_health():
    response = client.get("/health/")
    assert response.status_code == 200

def test_restaurant_list():
    assert isinstance(read_restaurants(), list)
    assert read_restaurants()[0]["id"] == 1