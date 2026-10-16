import json
from pathlib import Path
from typing import Any

# Store JSON files in the repository's data directory.
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

restaurant_file = DATA_DIR / "restaurants.json"
menu_file = DATA_DIR / "menus.json"
category_file = DATA_DIR / "categories.json"
item_file = DATA_DIR / "items.json"



def create_restaurant(record: dict[str, Any], data_file: Path = restaurant_file) -> dict[str, Any]:
    restaurants = read_restaurants(data_file)
    record_with_id = {"id": max((item["id"] for item in restaurants), default=0) + 1, **record}
    restaurants.append(record_with_id)
    with data_file.open("w", encoding="utf-8") as file:
        json.dump(restaurants, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return record_with_id


def read_menus(data_file: Path = menu_file) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)

def _read_records(data_file: Path) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)


def _write_records(data_file: Path, records: list[dict[str, Any]]) -> None:
    with data_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)


def read_restaurants(data_file: Path | None = None) -> list[dict[str, Any]]:
    return _read_records(data_file or restaurant_file)


def write_restaurants(records: list[dict[str, Any]], data_file: Path | None = None) -> None:
    _write_records(data_file or restaurant_file, records)


def read_menus(data_file: Path | None = None) -> list[dict[str, Any]]:
    return _read_records(data_file or menu_file)


def read_categories(data_file: Path | None = None) -> list[dict[str, Any]]:
    return _read_records(data_file or category_file)


def read_items(data_file: Path | None = None) -> list[dict[str, Any]]:
    return _read_records(data_file or item_file)


def write_items(records: list[dict[str, Any]], data_file: Path | None = None) -> None:
    _write_records(data_file or item_file, records)