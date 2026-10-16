from fastapi import APIRouter, HTTPException, status

from app.schemas import (
    Menu,
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
    Restaurant,
    RestaurantCreate,
    RestaurantUpdate,
)
from app.services.restaurant_service import (
    create_menu_item,
    create_restaurant,
    get_menu,
    get_menu_item,
    get_menu_items,
    get_menus,
    get_restaurant,
    list_restaurants,
    update_menu_item,
    update_restaurant,
)

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


# Customer endpoints for restaurant and menu lookups, plus restaurant creation.
@router.get("/health", response_model=dict)
def check_health():
    return {"status": "healthy"}


@router.get("/", response_model=list[Restaurant])
def read_restaurants(
    q: str | None = None,
    cuisine: str | None = None,
    min_rating: float | None = None,
    max_rating: float | None = None,
) -> list[Restaurant]:
    return list_restaurants(q, cuisine, min_rating, max_rating)


# Accepts validated restaurant details & returns record with  HTTP 201.
@router.post("/", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
def add_restaurant(restaurant: RestaurantCreate) -> Restaurant:
    return create_restaurant(restaurant)


@router.get("/{id}", response_model=Restaurant)
def read_restaurant(id: int) -> Restaurant:
    restaurant = get_restaurant(id)
    if restaurant is None:
        # A missing ID is a not-found response rather than empty restaurant.
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.put("/{id}", response_model=Restaurant)
@router.patch("/{id}", response_model=Restaurant)
def edit_restaurant(id: int, changes: RestaurantUpdate) -> Restaurant:
    restaurant = update_restaurant(id, changes)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.get("/{id}/menus", response_model=list[Menu])
def read_menus(id: int) -> list[Menu]:
    menus = get_menus(id)
    if not menus:
        raise HTTPException(status_code=404, detail="Menus not found")
    return menus


@router.get("/{restaurant_id}/menus/{menu_id}", response_model=Menu)
def read_menu(restaurant_id: int, menu_id: int) -> Menu:
    menu = get_menu(restaurant_id, menu_id)
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu


@router.get("/{restaurant_id}/menus/{menu_id}/items", response_model=list[MenuItem])
def read_menu_items(restaurant_id: int, menu_id: int) -> list[MenuItem]:
    if get_menu(restaurant_id, menu_id) is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    return get_menu_items(restaurant_id, menu_id)


@router.get("/{restaurant_id}/menu-items", response_model=list[MenuItem])
def read_restaurant_menu_items(restaurant_id: int) -> list[MenuItem]:
    if get_restaurant(restaurant_id) is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return get_menu_items(restaurant_id)


@router.post(
    "/{restaurant_id}/menu-items",
    response_model=MenuItem,
    status_code=status.HTTP_201_CREATED,
)
def add_menu_item(restaurant_id: int, item: MenuItemCreate) -> MenuItem:
    if get_restaurant(restaurant_id) is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    created_item = create_menu_item(restaurant_id, item)
    if created_item is None:
        raise HTTPException(status_code=404, detail="Menu category not found")
    return created_item


@router.get("/{restaurant_id}/menu-items/{item_id}", response_model=MenuItem)
def read_menu_item(restaurant_id: int, item_id: int) -> MenuItem:
    item = get_menu_item(restaurant_id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


@router.put("/{restaurant_id}/menu-items/{item_id}", response_model=MenuItem)
@router.patch("/{restaurant_id}/menu-items/{item_id}", response_model=MenuItem)
def edit_menu_item(
    restaurant_id: int, item_id: int, changes: MenuItemUpdate
) -> MenuItem:
    item = update_menu_item(restaurant_id, item_id, changes)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item or category not found")
    return item