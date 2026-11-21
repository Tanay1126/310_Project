from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.auth import get_current_customer
from app.schemas import (
    AuthToken,
    Cart,
    CartItemRequest,
    CartItemUpdate,
    Customer,
    CustomerCreate,
    CustomerLogin,
    CustomerUpdate,
    Order,
)
from app.services import customer_service
from app.services.customer_service import WorkflowError


router = APIRouter(prefix="/customers", tags=["customers"])


def _handle_workflow_error(error: WorkflowError) -> HTTPException:
    # Translate service workflow failures into consistent API responses.
    return HTTPException(status_code=error.status_code, detail=str(error))


@router.post(
    "/",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
    summary="Register a customer account",
    description="Creates an active customer account. Passwords are stored as salted PBKDF2 hashes.",
    responses={
        422: {"description": "Input validation failed"},
        409: {"description": "Email address is already registered"},
    },
)
def register_customer(customer: CustomerCreate) -> Customer:
    # Delegate account creation and return a public customer representation.
    try:
        return customer_service.register_customer(customer)
    except WorkflowError as error:
        raise _handle_workflow_error(error) from error


@router.post(
    "/login",
    response_model=AuthToken,
    summary="Sign in a customer",
    description="Returns a short-lived bearer token for protected customer operations.",
    responses={
        422: {"description": "Input validation failed"},
        401: {"description": "Invalid email or password"},
    },
)
def login_customer(credentials: CustomerLogin) -> AuthToken:
    # A successful sign-in returns both the bearer token and customer identity.
    try:
        token, customer = customer_service.sign_in(
            credentials.email, credentials.password
        )
    except WorkflowError as error:
        raise _handle_workflow_error(error) from error
    return AuthToken(access_token=token, customer=customer)


@router.get(
    "/me",
    response_model=Customer,
    summary="Get the signed-in customer",
    responses={401: {"description": "Authentication required"}},
)
def read_customer(customer: Customer = Depends(get_current_customer)) -> Customer:
    return customer


@router.patch(
    "/me",
    response_model=Customer,
    summary="Update customer information",
    responses={
        401: {"description": "Authentication required"},
        422: {"description": "Input validation failed"},
        409: {"description": "Email address is already registered"},
    },
)
def edit_customer(
    changes: CustomerUpdate,
    customer: Customer = Depends(get_current_customer),
) -> Customer:
    try:
        return customer_service.update_customer(customer.id, changes)
    except WorkflowError as error:
        raise _handle_workflow_error(error) from error


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate the signed-in customer",
    responses={401: {"description": "Authentication required"}},
)
def deactivate_customer(customer: Customer = Depends(get_current_customer)) -> Response:
    customer_service.deactivate_customer(customer.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/me/cart",
    response_model=Cart,
    summary="Get or create the active cart",
    responses={401: {"description": "Authentication required"}},
)
def read_cart(customer: Customer = Depends(get_current_customer)) -> Cart:
    # The service creates the customer's active cart when it does not exist.
    return customer_service.get_cart(customer.id)


@router.post(
    "/me/cart/items",
    response_model=Cart,
    summary="Add a menu item to the active cart",
    responses={
        401: {"description": "Authentication required"},
        404: {"description": "Menu item not found"},
        422: {"description": "Input validation failed"},
        409: {"description": "Item unavailable or cart belongs to another restaurant"},
    },
)
def add_cart_item(
    item: CartItemRequest,
    customer: Customer = Depends(get_current_customer),
) -> Cart:
    try:
        return customer_service.add_cart_item(
            customer.id, item.item_id, item.quantity
        )
    except WorkflowError as error:
        raise _handle_workflow_error(error) from error


@router.patch(
    "/me/cart/items/{item_id}",
    response_model=Cart,
    summary="Change a cart item quantity",
    responses={
        401: {"description": "Authentication required"},
        404: {"description": "Cart item not found"},
        422: {"description": "Input validation failed"},
    },
)
def edit_cart_item(
    item_id: int,
    changes: CartItemUpdate,
    customer: Customer = Depends(get_current_customer),
) -> Cart:
    try:
        return customer_service.update_cart_item(
            customer.id, item_id, changes.quantity
        )
    except WorkflowError as error:
        raise _handle_workflow_error(error) from error


@router.delete(
    "/me/cart/items/{item_id}",
    response_model=Cart,
    summary="Remove a cart item",
    responses={401: {"description": "Authentication required"}, 404: {"description": "Cart item not found"}},
)
def delete_cart_item(
    item_id: int,
    customer: Customer = Depends(get_current_customer),
) -> Cart:
    try:
        return customer_service.remove_cart_item(customer.id, item_id)
    except WorkflowError as error:
        raise _handle_workflow_error(error) from error


@router.delete(
    "/me/cart",
    response_model=Cart,
    summary="Clear the active cart",
    responses={401: {"description": "Authentication required"}},
)
def delete_cart(customer: Customer = Depends(get_current_customer)) -> Cart:
    return customer_service.clear_cart(customer.id)


@router.post(
    "/me/checkout",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Validate the cart and create an order",
    description=(
        "Revalidates the customer, current menu availability, and current prices. "
        "The cart is cleared only after the order is persisted."
    ),
    responses={
        401: {"description": "Authentication required"},
        409: {"description": "Cart is empty or contains an unavailable item"},
    },
)
def create_order(
    customer: Customer = Depends(get_current_customer),
) -> Order:
    # Checkout revalidates the cart and only clears it after order persistence.
    try:
        return customer_service.checkout(customer)
    except WorkflowError as error:
        raise _handle_workflow_error(error) from error


@router.get(
    "/me/orders",
    response_model=list[Order],
    summary="List the signed-in customer's orders",
    responses={401: {"description": "Authentication required"}},
)
def read_customer_orders(
    customer: Customer = Depends(get_current_customer),
) -> list[Order]:
    return customer_service.list_customer_orders(customer.id)


@router.get(
    "/me/orders/{order_id}",
    response_model=Order,
    summary="Get one of the signed-in customer's orders",
    responses={
        401: {"description": "Authentication required"},
        404: {"description": "Order not found"},
    },
)
def read_customer_order(
    order_id: int,
    customer: Customer = Depends(get_current_customer),
) -> Order:
    try:
        return customer_service.get_order_for_customer(customer.id, order_id)
    except WorkflowError as error:
        raise _handle_workflow_error(error) from error
