from fastapi.testclient import TestClient
import pytest
from app.repositories.restaurant_repository import read_restaurants, read_categories, read_items, read_menus
from app.main import app
import shutil
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

client = TestClient(app)

@pytest.fixture(autouse=True)
def isolated_data(tmp_path, monkeypatch):
    for name in {"restuarants.json", "items.json", "menus.json", "categories.json"}:
        shutil.copy(DATA_DIR / name, tmp_path / name)
    monkeypatch.setenv("test", str(tmp_path))

def test_read_restaurant():
    response = client.get("/restaurants/")
    assert response.status_code == 200

def test_read_restaurant_id():
    response = client.get("/restaurants/1")
    assert response.status_code == 200

def test_read_restaurant_id_not_found():
    response = client.get("/restaurants/999")
    assert response.status_code == 404

def test_get_health():
    response = client.get("/health/")
    assert response.status_code == 200

def test_restaurant_repository():
    assert read_restaurants[0][0] == 1

def test_items_repository():
    assert read_items[0][0] == 111

def test_menu_repository():
    assert read_menus[0][0] == 1

def test_gategory_repository():
    assert read_categories[0][0] == 11