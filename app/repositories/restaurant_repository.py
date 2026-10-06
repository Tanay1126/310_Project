import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

restaurant_file = DATA_DIR / "restaurants.json"
menu_file = DATA_DIR / "menus.json"
category_file = DATA_DIR / "categories.json"
item_file = DATA_DIR / "items.json"

def read_restaurants(data_file: Path = restaurant_file) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)

def read_menus(data_file: Path = menu_file) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)

def read_categories(data_file: Path = category_file) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)

def read_items(data_file: Path = item_file) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)