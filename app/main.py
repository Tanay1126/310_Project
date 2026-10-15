from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.routes.restaurants import router as restaurants_router

app = FastAPI()
app.include_router(restaurants_router)


@app.get("/")
def read_root():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health/")
def health_check():
    return {"status": "healthy"}