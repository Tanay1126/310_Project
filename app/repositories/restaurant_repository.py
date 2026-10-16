import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# JSON file locations and access in the repository, not in route handlers.
restaurant_file = DATA_DIR / "restaurants.json"
menu_file = DATA_DIR / "menus.json"
category_file = DATA_DIR / "categories.json"
item_file = DATA_DIR / "items.json"

def _read_records(data_file: Path) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)


def _write_records(data_file: Path, records: list[dict[str, Any]]) -> None:
    with data_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)
        file.write("\n")


def read_restaurants(data_file: Path | None = None) -> list[dict[str, Any]]:
    return _read_records(data_file if data_file is not None else restaurant_file)


def create_restaurant(
    record: dict[str, Any], data_file: Path | None = None
) -> dict[str, Any]:
    data_file = data_file if data_file is not None else restaurant_file
    restaurants = read_restaurants(data_file)
    record_with_id = {"id": max((item["id"] for item in restaurants), default=0) + 1, **record}
    restaurants.append(record_with_id)
    _write_records(data_file, restaurants)
    return record_with_id


def update_restaurant(
    restaurant_id: int, changes: dict[str, Any], data_file: Path | None = None
) -> dict[str, Any] | None:
    data_file = data_file if data_file is not None else restaurant_file
    restaurants = read_restaurants(data_file)
    restaurant = next((record for record in restaurants if record["id"] == restaurant_id), None)
    if restaurant is None:
        return None
    restaurant.update(changes)
    _write_records(data_file, restaurants)
    return restaurant


def read_menus(data_file: Path | None = None) -> list[dict[str, Any]]:
    return _read_records(data_file if data_file is not None else menu_file)


def read_categories(data_file: Path | None = None) -> list[dict[str, Any]]:
    return _read_records(data_file if data_file is not None else category_file)


def read_items(data_file: Path | None = None) -> list[dict[str, Any]]:
    return _read_records(data_file if data_file is not None else item_file)


def create_item(record: dict[str, Any], data_file: Path | None = None) -> dict[str, Any]:
    data_file = data_file if data_file is not None else item_file
    items = read_items(data_file)
    item_with_id = {"id": max((item["id"] for item in items), default=0) + 1, **record}
    items.append(item_with_id)
    _write_records(data_file, items)
    return item_with_id


def update_item(
    item_id: int, changes: dict[str, Any], data_file: Path | None = None
) -> dict[str, Any] | None:
    data_file = data_file if data_file is not None else item_file
    items = read_items(data_file)
    item = next((record for record in items if record["id"] == item_id), None)
    if item is None:
        return None
    item.update(changes)
    _write_records(data_file, items)
    return item