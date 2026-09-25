from fastapi import FastAPI

app = FastAPI(title="Restaurant API", version="1.0")

#Health Check Endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}


#Restaurant List Endpoint
@app.get("/restaurants")
def get_restaurants():
    restaurants = [
        {"id": 1, "name": "Sushi Place", "cuisine": "Japanese", "rating": 4.7},
        {"id": 2, "name": "Pasta House", "cuisine": "Italian", "rating": 4.5},
        {"id": 3, "name": "Burger Town", "cuisine": "American", "rating": 4.2},
    ]
    return {"restaurants": restaurants}
