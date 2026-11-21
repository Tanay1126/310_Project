from pydantic import BaseModel, Field, field_validator


class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str | None = None
    description: str | None = None
    rating: float | None = None


class RestaurantCreate(BaseModel):
    # Creation schemas apply constraints and normalize required text before persistence.
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


class RestaurantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    cuisine: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    rating: float | None = Field(default=None, ge=0, le=5)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Name must not be null")
        name = value.strip()
        if not name:
            raise ValueError("Name must not be blank")
        return name


class MenuItemCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    description: str | None = None
    ingredients: list[str] | None = None
    available: bool = True
    active: bool = True


class MenuItemUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, ge=0)
    description: str | None = None
    ingredients: list[str] | None = None
    available: bool | None = None
    active: bool | None = None

    @field_validator("category_id", "name", "price", "available", "active")
    @classmethod
    def required_fields_must_not_be_null(
        cls, value: int | str | float | bool | None
    ) -> int | str | float | bool | None:
        if value is None:
            raise ValueError("This field must not be null")
        return value


class MenuItem(BaseModel):
    category_id: int
    id: int
    name: str
    price: float
    description: str | None = None
    ingredients: list[str] | None = None
    available: bool = True
    active: bool = True

class MenuCategory(BaseModel):
    menu_id: int
    id: int
    name: str
    description: str | None = None
    items: list[MenuItem] | None = None    

class Menu(BaseModel):
    restaurant_id: int
    id: int
    name: str
    categories: list[MenuCategory] | None = None


class CustomerCreate(BaseModel):
    # Customer input is trimmed and email addresses are normalized consistently.
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    delivery_address: str = Field(min_length=1, max_length=500)

    @field_validator("name", "email", "delivery_address")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field must not be blank")
        return normalized

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        email = value.casefold()
        if email.count("@") != 1 or "." not in email.rsplit("@", maxsplit=1)[-1]:
            raise ValueError("A valid email address is required")
        return email


class CustomerLogin(BaseModel):
    # Login normalization ensures email matching is case-insensitive.
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        email = value.strip().casefold()
        if email.count("@") != 1 or "." not in email.rsplit("@", maxsplit=1)[-1]:
            raise ValueError("A valid email address is required")
        return email


class CustomerUpdate(BaseModel):
    # Update fields reject null values so optional fields cannot erase data accidentally.
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    delivery_address: str | None = Field(default=None, min_length=1, max_length=500)

    @field_validator("name", "email", "delivery_address")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("This field must not be null")
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field must not be blank")
        return normalized

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        email = value.casefold()
        if email.count("@") != 1 or "." not in email.rsplit("@", maxsplit=1)[-1]:
            raise ValueError("A valid email address is required")
        return email


class Customer(BaseModel):
    id: int
    name: str
    email: str
    delivery_address: str
    role: str = "customer"
    active: bool = True


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    customer: Customer


class CartItemRequest(BaseModel):
    item_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=99)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=99)


class CartLine(BaseModel):
    item_id: int
    name: str
    unit_price: float
    quantity: int
    line_total: float


class Cart(BaseModel):
    # The cart response exposes calculated totals as well as restaurant ownership.
    id: int
    customer_id: int
    restaurant_id: int | None = None
    items: list[CartLine]
    subtotal: float
    total: float


class Order(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    customer_name: str
    delivery_address: str
    items: list[CartLine]
    subtotal: float
    total: float
    status: str = "placed"


