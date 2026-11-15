import json
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
customer_file = DATA_DIR / "customers.json"
cart_file = DATA_DIR / "carts.json"
order_file = DATA_DIR / "orders.json"


def _read_records(data_file: Path) -> list[dict[str, Any]]:
    with data_file.open(encoding="utf-8") as file:
        return json.load(file)


def _write_records(data_file: Path, records: list[dict[str, Any]]) -> None:
    with data_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)
        file.write("\n")


def read_customers() -> list[dict[str, Any]]:
    return _read_records(customer_file)


def get_customer(customer_id: int) -> dict[str, Any] | None:
    return next(
        (record for record in read_customers() if record["id"] == customer_id),
        None,
    )


def get_customer_by_email(email: str) -> dict[str, Any] | None:
    return next(
        (record for record in read_customers() if record["email"] == email),
        None,
    )


def create_customer(record: dict[str, Any]) -> dict[str, Any]:
    customers = read_customers()
    customer = {
        "id": max((record["id"] for record in customers), default=0) + 1,
        **record,
    }
    customers.append(customer)
    _write_records(customer_file, customers)
    return customer


def update_customer(
    customer_id: int, changes: dict[str, Any]
) -> dict[str, Any] | None:
    customers = read_customers()
    customer = next(
        (record for record in customers if record["id"] == customer_id),
        None,
    )
    if customer is None:
        return None
    customer.update(changes)
    _write_records(customer_file, customers)
    return customer


def get_cart(customer_id: int) -> dict[str, Any] | None:
    return next(
        (record for record in _read_records(cart_file) if record["customer_id"] == customer_id),
        None,
    )


def save_cart(cart: dict[str, Any]) -> dict[str, Any]:
    carts = _read_records(cart_file)
    existing = next(
        (record for record in carts if record["customer_id"] == cart["customer_id"]),
        None,
    )
    if existing is None:
        cart = {
            "id": max((record["id"] for record in carts), default=0) + 1,
            **cart,
        }
        carts.append(cart)
    else:
        cart = {**cart, "id": existing["id"]}
        existing.update(cart)
    _write_records(cart_file, carts)
    return cart


def create_order(order: dict[str, Any]) -> dict[str, Any]:
    orders = _read_records(order_file)
    order = {
        "id": max((record["id"] for record in orders), default=0) + 1,
        **order,
    }
    orders.append(order)
    _write_records(order_file, orders)
    return order


def get_order(order_id: int) -> dict[str, Any] | None:
    return next(
        (record for record in _read_records(order_file) if record["id"] == order_id),
        None,
    )


def get_customer_orders(customer_id: int) -> list[dict[str, Any]]:
    return [
        record
        for record in _read_records(order_file)
        if record["customer_id"] == customer_id
    ]
