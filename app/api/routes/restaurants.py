from fastapi import APIRouter, HTTPException, status

from app.schemas import Restaurant, RestaurantCreate, Menu
from app.services.restaurant_service import create_restaurant, get_restaurant, list_restaurants, get_menus

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


# Customer-facing endpoints for restaurant and menu lookups, plus restaurant creation.
@router.get("/health", response_model=dict)
def check_health():
    return {"status": "healthy"}


@router.get("/", response_model=list[Restaurant])
def read_restaurants() -> list[Restaurant]:
    return list_restaurants()


# Accepts validated restaurant details and returns the created record with HTTP 201.
@router.post("/", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
def add_restaurant(restaurant: RestaurantCreate) -> Restaurant:
    return create_restaurant(restaurant)


@router.get("/{id}", response_model=Restaurant)
def read_restaurant(id: int) -> Restaurant:
    restaurant = get_restaurant(id)
    if restaurant is None:
        # A missing ID is a not-found response rather than an empty restaurant.
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.get("/{id}/menus", response_model=list[Menu])
def read_menus(id: int) -> list[Menu]:
    menus = get_menus(id)
    if not menus:
        raise HTTPException(status_code=404, detail="Menus not found")
    return menus