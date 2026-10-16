from app.repositories.restaurant_repository import (
    create_item as save_item,
    create_restaurant as save_restaurant,
    read_categories,
    read_items,
    read_menus,
    read_restaurants,
    update_item as save_item_update,
    update_restaurant as save_restaurant_update,
)
from app.schemas import (
    Menu,
    MenuCategory,
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
    Restaurant,
    RestaurantCreate,
    RestaurantUpdate,
)


def list_restaurants(
    q: str | None = None,
    cuisine: str | None = None,
    min_rating: float | None = None,
    max_rating: float | None = None,
) -> list[Restaurant]:
    # Convert repository dictionaries into validated API models.
    restaurants = [Restaurant.model_validate(record) for record in read_restaurants()]
    if q:
        query = q.casefold()
        restaurants = [
            restaurant
            for restaurant in restaurants
            if any(
                query in (value or "").casefold()
                for value in (restaurant.name, restaurant.cuisine, restaurant.description)
            )
        ]
    if cuisine:
        cuisine_filter = cuisine.casefold()
        restaurants = [
            restaurant
            for restaurant in restaurants
            if cuisine_filter in (restaurant.cuisine or "").casefold()
        ]
    if min_rating is not None:
        restaurants = [
            restaurant
            for restaurant in restaurants
            if restaurant.rating is not None and restaurant.rating >= min_rating
        ]
    if max_rating is not None:
        restaurants = [
            restaurant
            for restaurant in restaurants
            if restaurant.rating is not None and restaurant.rating <= max_rating
        ]
    return restaurants


def get_restaurant(restaurant_id: int) -> Restaurant | None:
    # Return None when the ID is unknown so the route responds 404.
    return next(
        (restaurant for restaurant in list_restaurants() if restaurant.id == restaurant_id),
        None,
    )


def create_restaurant(restaurant: RestaurantCreate) -> Restaurant:
    record = save_restaurant(restaurant.model_dump(exclude_none=True))
    return Restaurant.model_validate(record)


def update_restaurant(
    restaurant_id: int, restaurant: RestaurantUpdate
) -> Restaurant | None:
    record = save_restaurant_update(
        restaurant_id,
        restaurant.model_dump(exclude_unset=True),
    )
    return Restaurant.model_validate(record) if record is not None else None


def get_menus(restaurant_id: int) -> list[Menu]:
    # Process: restaurant -> menu -> category -> item IDs.
    menus = [Menu.model_validate(menu) for menu in read_menus() if menu["restaurant_id"] == restaurant_id]

    menu_ids = [menu.id for menu in menus]
    menu_categories = [MenuCategory.model_validate(category) for category in read_categories() if category["menu_id"] in menu_ids]
    category_ids = [categories.id for categories in menu_categories]
    menu_items = [MenuItem.model_validate(item) for item in read_items() if item["category_id"] in category_ids]

    # Attach each item's records to its category, then each category to menu.
    for category in menu_categories:
        category.items = [item for item in menu_items if item.category_id == category.id]

    for menu in menus:
        menu.categories = [category for category in menu_categories if category.menu_id == menu.id]

    return menus


def get_menu(restaurant_id: int, menu_id: int) -> Menu | None:
    return next(
        (menu for menu in get_menus(restaurant_id) if menu.id == menu_id),
        None,
    )


def get_menu_items(restaurant_id: int, menu_id: int | None = None) -> list[MenuItem]:
    menus = get_menus(restaurant_id)
    if menu_id is not None:
        menus = [menu for menu in menus if menu.id == menu_id]
    category_ids = {
        category.id
        for menu in menus
        for category in menu.categories or []
    }
    return [
        MenuItem.model_validate(item)
        for item in read_items()
        if item["category_id"] in category_ids
    ]


def get_menu_item(restaurant_id: int, item_id: int) -> MenuItem | None:
    return next(
        (item for item in get_menu_items(restaurant_id) if item.id == item_id),
        None,
    )


def create_menu_item(restaurant_id: int, item: MenuItemCreate) -> MenuItem | None:
    category = next(
        (category for category in read_categories() if category["id"] == item.category_id),
        None,
    )
    if category is None or get_menu(restaurant_id, category["menu_id"]) is None:
        return None
    return MenuItem.model_validate(save_item(item.model_dump()))


def update_menu_item(
    restaurant_id: int, item_id: int, item: MenuItemUpdate
) -> MenuItem | None:
    if get_menu_item(restaurant_id, item_id) is None:
        return None
    changes = item.model_dump(exclude_unset=True)
    category_id = changes.get("category_id")
    if category_id is not None:
        category = next(
            (record for record in read_categories() if record["id"] == category_id),
            None,
        )
        if category is None or get_menu(restaurant_id, category["menu_id"]) is None:
            return None
    record = save_item_update(item_id, changes)
    return MenuItem.model_validate(record) if record is not None else None