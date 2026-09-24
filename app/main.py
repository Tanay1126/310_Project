from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str | None = None
    description: str | None = None
    rating: float | None = None

# temporary test data for restaurants
restaurants = [
    Restaurant(id=1, name="test restaurant 1", cuisine="Italian", description="test desc 1", rating=4.5),
    Restaurant(id=2, name="test restaurant 2", cuisine="Japanese", description="test desc 2", rating=4.7)
]

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/restaurants/", response_model=list[Restaurant])
def get_restaurants():
    return restaurants

@app.get("/restaurants/{id}", response_model=Restaurant)
def read_restaurant(id: int):
    return restaurants[id]