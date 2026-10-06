from pydantic import BaseModel


class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str | None = None
    description: str | None = None
    rating: float | None = None

class Menu(BaseModel):
    restaurant_id: int
    id: int
    name: str
    categories: list[MenuCategory] | None = None

class MenuCategory(BaseModel):
    menu_id: int
    id: int
    name: str
    description: str | None = None
    items: list[MenuItem] | None = None

class MenuItem(BaseModel):
    category_id: int
    id: int
    name: str
    price: float
    description: str | None = None
    ingredients: list[str] | None = None