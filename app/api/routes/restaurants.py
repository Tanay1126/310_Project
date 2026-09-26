from fastapi import APIRouter, HTTPException

from app.schemas import Restaurant
from app.services.restaurant_service import get_restaurant, list_restaurants

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("/health", response_model=dict)
def check_health():
    return {"status": "healthy"}

@router.get("/", response_model=list[Restaurant])
def read_restaurants() -> list[Restaurant]:
    return list_restaurants()

@router.get("/{id}", response_model=Restaurant)
def read_restaurant(id: int) -> Restaurant:
    restaurant = get_restaurant(id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant