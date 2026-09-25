from pydantic import BaseModel


class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str
    description: str
    rating: float