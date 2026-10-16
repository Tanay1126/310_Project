import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Keep JSON file locations and access in the repository, not in route handlers.
restaurant_file = DATA_DIR / "restaurants.json"
menu_file = DATA_DIR / "menus.json"
category_file = DATA_DIR / "categories.json"
item_file = DATA_DIR / "items.json"

def read_restaurants(data_file: Path = restaurant_file) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)


def create_restaurant(record: dict[str, Any], data_file: Path = restaurant_file) -> dict[str, Any]:
    restaurants = read_restaurants(data_file)
    # Assign one more than the current highest ID; use 1 when the file is empty.
    record_with_id = {"id": max((item["id"] for item in restaurants), default=0) + 1, **record}
    restaurants.append(record_with_id)
    with data_file.open("w", encoding="utf-8") as file:
        json.dump(restaurants, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return record_with_id


def read_menus(data_file: Path = menu_file) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)

def read_categories(data_file: Path = category_file) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)

def read_items(data_file: Path = item_file) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)