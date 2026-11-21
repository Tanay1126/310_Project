from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from app.auth import create_access_token, hash_password, verify_password
from app.repositories import workflow_repository
from app.schemas import (
    Cart,
    CartLine,
    Customer,
    CustomerCreate,
    CustomerUpdate,
    Order,
)
from app.services.restaurant_service import get_menu_item_context


class WorkflowError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


def _public_customer(record: dict[str, Any]) -> Customer:
    # Password fields are repository data and must not appear in API responses.
    return Customer.model_validate(
        {key: value for key, value in record.items() if not key.startswith("password_")}
    )


def register_customer(customer: CustomerCreate) -> Customer:
    # Reject duplicate emails before hashing and saving a new customer.
    if workflow_repository.get_customer_by_email(customer.email) is not None:
        raise WorkflowError("An account with this email already exists", 409)
    password_fields = hash_password(customer.password)
    record = workflow_repository.create_customer(
        {
            "name": customer.name,
            "email": customer.email,
            "delivery_address": customer.delivery_address,
            "role": "customer",
            "active": True,
            **password_fields,
        }
    )
    return _public_customer(record)


def sign_in(email: str, password: str) -> tuple[str, Customer]:
    # Authentication requires an active account and a matching password hash.
    record = workflow_repository.get_customer_by_email(email)
    if (
        record is None
        or not record["active"]
        or not verify_password(password, record)
    ):
        raise WorkflowError("Invalid email or password", 401)
    customer = _public_customer(record)
    return create_access_token(customer.id, customer.role), customer


def update_customer(
    customer_id: int, changes: CustomerUpdate
) -> Customer:
    # Only fields explicitly supplied in the update should be persisted.
    fields = changes.model_dump(exclude_unset=True)
    if "email" in fields:
        existing = workflow_repository.get_customer_by_email(fields["email"])
        if existing is not None and existing["id"] != customer_id:
            raise WorkflowError("An account with this email already exists", 409)
    record = workflow_repository.update_customer(customer_id, fields)
    if record is None:
        raise WorkflowError("Customer not found", 404)
    return _public_customer(record)


def deactivate_customer(customer_id: int) -> None:
    # Deactivation preserves the account record while preventing future sign-in.
    record = workflow_repository.update_customer(customer_id, {"active": False})
    if record is None:
        raise WorkflowError("Customer not found", 404)


def _get_or_create_cart(customer_id: int) -> dict[str, Any]:
    # Customers receive an empty cart automatically on their first cart operation.
    cart = workflow_repository.get_cart(customer_id)
    if cart is not None:
        return cart
    return workflow_repository.save_cart(
        {"customer_id": customer_id, "restaurant_id": None, "items": []}
    )


def _money(value: float) -> float:
    # Round every monetary calculation consistently to two decimal places.
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def get_cart(customer_id: int) -> Cart:
    # Rebuild cart lines from current menu records rather than cached prices.
    cart = _get_or_create_cart(customer_id)
    lines: list[CartLine] = []
    for entry in cart["items"]:
        context = get_menu_item_context(entry["item_id"])
        if context is None:
            raise WorkflowError("A cart item no longer exists", 409)
        item, _ = context
        unit_price = _money(item.price)
        lines.append(
            CartLine(
                item_id=item.id,
                name=item.name,
                unit_price=unit_price,
                quantity=entry["quantity"],
                line_total=_money(unit_price * entry["quantity"]),
            )
        )
    subtotal = _money(sum(line.line_total for line in lines))
    return Cart(
        id=cart["id"],
        customer_id=customer_id,
        restaurant_id=cart["restaurant_id"],
        items=lines,
        subtotal=subtotal,
        total=subtotal,
    )


def add_cart_item(customer_id: int, item_id: int, quantity: int) -> Cart:
    # Validate menu availability and restaurant ownership before changing the cart.
    context = get_menu_item_context(item_id)
    if context is None:
        raise WorkflowError("Menu item not found", 404)
    item, restaurant_id = context
    if not item.active or not item.available:
        raise WorkflowError("Menu item is unavailable", 409)
    cart = _get_or_create_cart(customer_id)
    if cart["items"] and cart["restaurant_id"] != restaurant_id:
        raise WorkflowError("A cart can contain items from only one restaurant", 409)
    existing = next(
        (entry for entry in cart["items"] if entry["item_id"] == item_id),
        None,
    )
    # Merge the quantity into an existing line instead of duplicating it.
    if existing is not None:
        if existing["quantity"] + quantity > 99:
            raise WorkflowError("Item quantity cannot exceed 99", 422)
        existing["quantity"] += quantity
    else:
        cart["items"].append({"item_id": item_id, "quantity": quantity})
    cart["restaurant_id"] = restaurant_id
    workflow_repository.save_cart(cart)
    return get_cart(customer_id)


def update_cart_item(customer_id: int, item_id: int, quantity: int) -> Cart:
    cart = _get_or_create_cart(customer_id)
    entry = next(
        (item for item in cart["items"] if item["item_id"] == item_id),
        None,
    )
    if entry is None:
        raise WorkflowError("Cart item not found", 404)
    entry["quantity"] = quantity
    workflow_repository.save_cart(cart)
    return get_cart(customer_id)


def remove_cart_item(customer_id: int, item_id: int) -> Cart:
    # Clearing the final item also releases the cart's restaurant restriction.
    cart = _get_or_create_cart(customer_id)
    remaining = [entry for entry in cart["items"] if entry["item_id"] != item_id]
    if len(remaining) == len(cart["items"]):
        raise WorkflowError("Cart item not found", 404)
    cart["items"] = remaining
    if not remaining:
        cart["restaurant_id"] = None
    workflow_repository.save_cart(cart)
    return get_cart(customer_id)


def clear_cart(customer_id: int) -> Cart:
    cart = _get_or_create_cart(customer_id)
    cart["items"] = []
    cart["restaurant_id"] = None
    workflow_repository.save_cart(cart)
    return get_cart(customer_id)


def checkout(customer: Customer) -> Order:
    # Revalidate the cart and current menu before persisting an order snapshot.
    cart = _get_or_create_cart(customer.id)
    if not cart["items"]:
        raise WorkflowError("Cannot check out an empty cart", 409)
    if not customer.active:
        raise WorkflowError("Inactive customers cannot check out", 403)

    lines: list[CartLine] = []
    for entry in cart["items"]:
        context = get_menu_item_context(entry["item_id"])
        if context is None:
            raise WorkflowError("A cart item no longer exists", 409)
        item, restaurant_id = context
        if restaurant_id != cart["restaurant_id"]:
            raise WorkflowError("Cart contains an item from another restaurant", 409)
        if not item.active or not item.available:
            raise WorkflowError(f"{item.name} is no longer available", 409)
        unit_price = _money(item.price)
        lines.append(
            CartLine(
                item_id=item.id,
                name=item.name,
                unit_price=unit_price,
                quantity=entry["quantity"],
                line_total=_money(unit_price * entry["quantity"]),
            )
        )
    subtotal = _money(sum(line.line_total for line in lines))
    # Persist a snapshot of names and prices before clearing the customer's cart.
    order_record = workflow_repository.create_order(
        {
            "customer_id": customer.id,
            "restaurant_id": cart["restaurant_id"],
            "customer_name": customer.name,
            "delivery_address": customer.delivery_address,
            "items": [line.model_dump() for line in lines],
            "subtotal": subtotal,
            "total": subtotal,
            "status": "placed",
        }
    )
    cart["items"] = []
    cart["restaurant_id"] = None
    workflow_repository.save_cart(cart)
    return Order.model_validate(order_record)


def get_order_for_customer(customer_id: int, order_id: int) -> Order:
    order = workflow_repository.get_order(order_id)
    if order is None or order["customer_id"] != customer_id:
        raise WorkflowError("Order not found", 404)
    return Order.model_validate(order)


def list_customer_orders(customer_id: int) -> list[Order]:
    return [
        Order.model_validate(order)
        for order in workflow_repository.get_customer_orders(customer_id)
    ]
