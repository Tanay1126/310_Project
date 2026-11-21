from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.routes.customers import router as customers_router
from app.api.routes.restaurants import router as restaurants_router

app = FastAPI(
    title="Restaurant Ordering API",
    version="1.0.0",
    description=(
        "Browse restaurants and menus, manage a customer cart, and place orders. "
        "Customer cart and order operations require a bearer token."
    ),
    openapi_tags=[
        {
            "name": "restaurants",
            "description": "Restaurant, menu, category, and menu-item discovery and management.",
        },
        {
            "name": "customers",
            "description": "Customer registration and authentication, cart management, and order access.",
        },
    ],
)
app.include_router(restaurants_router)
app.include_router(customers_router)


@app.get("/")
def read_root():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health/")
def health_check():
    return {"status": "healthy"}