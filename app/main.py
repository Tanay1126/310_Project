from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.routes.customers import router as customers_router
from app.api.routes.restaurants import router as restaurants_router

app = FastAPI(
    title="Restaurant Ordering API",
    description=(
        "Browse restaurants and menus, manage a customer cart, and place orders. "
        "Customer cart and order operations require a bearer token."
    ),
)
app.include_router(restaurants_router)
app.include_router(customers_router)


@app.get("/")
def read_root():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health/")
def health_check():
    return {"status": "healthy"}