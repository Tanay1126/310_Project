from fastapi import FastAPI

from app.api.routes.restaurants import router as restaurants_router

app = FastAPI()
app.include_router(restaurants_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
