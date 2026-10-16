from app.repositories.restaurant_repository import create_restaurant as save_restaurant
from app.repositories.restaurant_repository import read_restaurants, read_menus, read_categories, read_items
from app.schemas import Restaurant, RestaurantCreate, Menu, MenuCategory, MenuItem


def list_restaurants(
    query: str | None = None,
    cuisine: str | None = None,
    min_rating: float | None = None,
    max_rating: float | None = None,
) -> list[Restaurant]:
    # Load records,then apply the requested search and rating filters.
    restaurants = [Restaurant.model_validate(record) for record in read_restaurants()]
    if query:
        search = query.casefold()
        restaurants = [
            restaurant
            for restaurant in restaurants
            if search in restaurant.name.casefold()
            or search in (restaurant.cuisine or "").casefold()
            or search in (restaurant.description or "").casefold()
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
    # Return the matching restaurant, or None when DNE.
    return next(
        (restaurant for restaurant in list_restaurants() if restaurant.id == restaurant_id),
        None,
    )


def create_restaurant(restaurant: RestaurantCreate) -> Restaurant:
    record = save_restaurant(restaurant.model_dump(exclude_none=True))
    return Restaurant.model_validate(record)


def get_menus(restaurant_id: int) -> list[Menu]:
    # Assemble menus with their categories and items for restaurant
    menus = [
        Menu.model_validate(menu)
        for menu in read_menus()
        if menu["restaurant_id"] == restaurant_id
    ]

    menu_ids = [menu.id for menu in menus]
    menu_categories = [
        MenuCategory.model_validate(category)
        for category in read_categories()
        if category["menu_id"] in menu_ids
    ]
    category_ids = [categories.id for categories in menu_categories]
    menu_items = [
        MenuItem.model_validate(item)
        for item in read_items()
        if item["category_id"] in category_ids
    ]

    for category in menu_categories:
        category.items = [item for item in menu_items if item.category_id == category.id]

    for menu in menus:
        menu.categories = [category for category in menu_categories if category.menu_id == menu.id]

    return menus


def get_menu_items(restaurant_id: int) -> list[MenuItem]:
    # Flatten/ Shrink items in restaurant categories
    return [
        item
        for menu in get_menus(restaurant_id)
        for category in menu.categories or []
        for item in category.items or []
    ]


def create_menu_item(
    restaurant_id: int, payload: MenuItemCreate
) -> MenuItem | None:
    # Only add an item when its category belongs to this restaurant.
    category = next(
        (
            category
            for menu in get_menus(restaurant_id)
            for category in menu.categories or []
            if category.id == payload.category_id
        ),
        None,
    )
    if category is None:
        return None

    records = read_items()
    item = MenuItem(
        id=max((record["id"] for record in records), default=0) + 1,
        **payload.model_dump(),
    )
    records.append(item.model_dump())
    write_items(records)
    return item


def update_menu_item(
    restaurant_id: int, item_id: int, changes: dict[str, object]
) -> MenuItem | None:
    # Verify the item belongs to this restaurant before updating.
    item_ids = {item.id for item in get_menu_items(restaurant_id)}
    if item_id not in item_ids:
        return None

    records = read_items()
    for record in records:
        if record["id"] == item_id:
            record.update(changes)
            write_items(records)
            return MenuItem.model_validate(record)
    return None


def get_menu(restaurant_id: int, menu_id: int) -> Menu | None:
    # Find one menu within the restaurant's assembled menus
    return next((menu for menu in get_menus(restaurant_id) if menu.id == menu_id), None)