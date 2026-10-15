from pydantic import BaseModel


class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str | None = None
    description: str | None = None
    rating: float | None = None


class RestaurantCreate(BaseModel):
    name: str
    cuisine: str | None = None
    description: str | None = None
    rating: float | None = None


class RestaurantUpdate(BaseModel):
    name: str | None = None
    cuisine: str | None = None
    description: str | None = None
    rating: float | None = None


