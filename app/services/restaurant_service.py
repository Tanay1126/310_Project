from app.repositories.restaurant_repository import read_restaurants
from app.schemas import Restaurant


def list_restaurants() -> list[Restaurant]:
    return [Restaurant.model_validate(record) for record in read_restaurants()]


def get_restaurant(restaurant_id: int) -> Restaurant | None:
    return next(
        (restaurant for restaurant in list_restaurants() if restaurant.id == restaurant_id),
        None,
    )