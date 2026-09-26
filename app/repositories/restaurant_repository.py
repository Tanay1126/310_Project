import json
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "restaurants.json"


def read_restaurants(data_file: Path = DATA_FILE) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)