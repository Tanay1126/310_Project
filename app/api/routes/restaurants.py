from fastapi import APIRouter, HTTPException, Query

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
    get_menu_items,
    get_menus,
    get_restaurant,
    list_restaurants,
    update_menu_item,
    update_restaurant,
)

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("/health", response_model=dict)
def check_health():
    return {"status": "healthy"}


@router.get("/", response_model=list[Restaurant])
def read_restaurants(
    q: str | None = None,
    cuisine: str | None = None,
    min_rating: float | None = Query(default=None, ge=0, le=5),
    max_rating: float | None = Query(default=None, ge=0, le=5),
) -> list[Restaurant]:
    # Reject contradictory rating bounds before filtering.
    if min_rating is not None and max_rating is not None and min_rating > max_rating:
        raise HTTPException(status_code=422, detail="min_rating cannot exceed max_rating")
    return list_restaurants(q, cuisine, min_rating, max_rating)


@router.post("/", response_model=Restaurant, status_code=201)
def create_restaurant_record(payload: RestaurantCreate) -> Restaurant:
    return create_restaurant(payload)



@router.post("/", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
def add_restaurant(restaurant: RestaurantCreate) -> Restaurant:
    return create_restaurant(restaurant)


@router.get("/{id}", response_model=Restaurant)
def read_restaurant(id: int) -> Restaurant:
    restaurant = get_restaurant(id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.patch("/{id}", response_model=Restaurant)
@router.put("/{id}", response_model=Restaurant)
def update_restaurant_record(id: int, payload: RestaurantUpdate) -> Restaurant:
    changes = payload.model_dump(exclude_unset=True)
    # PATCH fields omitted by the caller are not included in changes.
    if any(changes.get(field) is None for field in ("name",) if field in changes):
        raise HTTPException(status_code=422, detail="name cannot be null")
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
    menu = get_menu(restaurant_id, menu_id)
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    return [
        item
        for category in menu.categories or []
        for item in category.items or []
    ]


@router.get("/{restaurant_id}/menu-items", response_model=list[MenuItem])
def read_restaurant_menu_items(restaurant_id: int) -> list[MenuItem]:
    if get_restaurant(restaurant_id) is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return get_menu_items(restaurant_id)


@router.get("/{restaurant_id}/menu-items/{item_id}", response_model=MenuItem)
def read_menu_item(restaurant_id: int, item_id: int) -> MenuItem:
    item = next(
        (item for item in get_menu_items(restaurant_id) if item.id == item_id),
        None,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


@router.post("/{restaurant_id}/menu-items", response_model=MenuItem, status_code=201)
def create_menu_item_record(restaurant_id: int, payload: MenuItemCreate) -> MenuItem:
    if get_restaurant(restaurant_id) is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    item = create_menu_item(restaurant_id, payload)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu category not found")
    return item


@router.patch("/{restaurant_id}/menu-items/{item_id}", response_model=MenuItem)
@router.put("/{restaurant_id}/menu-items/{item_id}", response_model=MenuItem)
def update_menu_item_record(
    restaurant_id: int, item_id: int, payload: MenuItemUpdate
) -> MenuItem:
    changes = payload.model_dump(exclude_unset=True)
    if any(changes.get(field) is None for field in ("name", "price") if field in changes):
        raise HTTPException(status_code=422, detail="name and price cannot be null")
    item = update_menu_item(restaurant_id, item_id, changes)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item