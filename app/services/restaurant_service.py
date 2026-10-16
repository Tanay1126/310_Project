from app.repositories.restaurant_repository import create_restaurant as save_restaurant
from app.repositories.restaurant_repository import read_restaurants, read_menus, read_categories, read_items
from app.schemas import Restaurant, RestaurantCreate, Menu, MenuCategory, MenuItem


def list_restaurants() -> list[Restaurant]:
    # Convert repository dictionaries into validated API models.
    return [Restaurant.model_validate(record) for record in read_restaurants()]


def get_restaurant(restaurant_id: int) -> Restaurant | None:
    # Return None when the ID is unknown so the route responds 404.
    return next(
        (restaurant for restaurant in list_restaurants() if restaurant.id == restaurant_id),
        None,
    )


def create_restaurant(restaurant: RestaurantCreate) -> Restaurant:
    record = save_restaurant(restaurant.model_dump(exclude_none=True))
    return Restaurant.model_validate(record)


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