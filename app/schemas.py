from pydantic import BaseModel, Field, field_validator


class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str | None = None
    description: str | None = None
    rating: float | None = None


class RestaurantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    cuisine: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    rating: float | None = Field(default=None, ge=0, le=5)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        # Reject whitespace-only names before saving.
        name = value.strip()
        if not name:
            raise ValueError("Name must not be blank")
        return name

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

    

class Menu(BaseModel):
    restaurant_id: int
    id: int
    name: str
    categories: list[MenuCategory] | None = None



