import json
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "restaurants.json"


def read_restaurants() -> list[dict[str, Any]]:
    with DATA_FILE.open(encoding="utf-8") as data_file:
        return json.load(data_file)