from app.repositories.restaurant_repository import read_restaurants, read_menus, read_categories, read_items
from app.schemas import Restaurant, Menu, MenuCategory, MenuItem


def list_restaurants() -> list[Restaurant]:
    return [Restaurant.model_validate(record) for record in read_restaurants()]


def get_restaurant(restaurant_id: int) -> Restaurant | None:
    return next(
        (restaurant for restaurant in list_restaurants() if restaurant.id == restaurant_id),
        None,
    )


def get_menus(restaurant_id: int) -> list[Menu]:
    menus = [Menu.model_validate(menu) for menu in read_menus() if menu["restaurant_id"] == restaurant_id]

    menu_ids = [menu.id for menu in menus]
    menu_categories = [MenuCategory.model_validate(category) for category in read_categories() if category["menu_id"] in menu_ids]
    category_ids = [categories.id for categories in menu_categories]
    menu_items = [MenuItem.model_validate(item) for item in read_items() if item["category_id"] in category_ids]

    for category in menu_categories:
        category.items = [item for item in menu_items if item.category_id == category.id]

    for menu in menus: 
        menu.categories = [category for category in menu_categories if category.menu_id == menu.id]

    return menus