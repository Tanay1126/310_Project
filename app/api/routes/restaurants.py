from fastapi import APIRouter, HTTPException

from app.schemas import Restaurant
from app.services.restaurant_service import get_restaurant, list_restaurants

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("/", response_model=list[Restaurant])
def read_restaurants() -> list[Restaurant]:
    return list_restaurants()


@router.get("/{restaurant_id}", response_model=Restaurant)
def read_restaurant(restaurant_id: int) -> Restaurant:
    restaurant = get_restaurant(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant