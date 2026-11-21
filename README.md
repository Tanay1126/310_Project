# COSC 310 Project

Team
Unit Test Failed

Version:
Python 3.14 or higher

Setup Instructions:
From the repository root, create and activate a virtual environment.

Windows PowerShell:

```powershell
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```sh
python3.14 -m venv .venv
source .venv/bin/activate
```

Dependency installation:
From the repository root, with the virtual enviroment active:

pip install -r requirements.txt


Run the application:
From the repository root, with the virtual environment active:

python -m uvicorn app.main:app --reload


The frontend and API are available at `http://127.0.0.1:8000`. Interactive Swagger documentation is at [`/docs`](http://127.0.0.1:8000/docs).

API endpoints:
`GET /` and `GET /health/` -> Health checks
`GET /restaurants/` -> List restaurants; supports `q`, `cuisine`, `min_rating`, and `max_rating` filters
`POST /restaurants/` -> Create a restaurant
`GET /restaurants/{restaurant_id}` -> Get a restaurant by ID
`PUT/PATCH /restaurants/{restaurant_id}` -> Update restaurant information
`GET /restaurants/{restaurant_id}/menus` -> Get a restaurant's menus, categories, and menu items
`GET /restaurants/{restaurant_id}/menus/{menu_id}` -> Get one menu
`GET /restaurants/{restaurant_id}/menus/{menu_id}/items` -> List items on a menu
`GET /restaurants/{restaurant_id}/menu-items` -> List all menu items for a restaurant
`GET /restaurants/{restaurant_id}/menu-items/{item_id}` -> Get one menu item
`POST /restaurants/{restaurant_id}/menu-items` -> Add a menu item (provide its `category_id`)
`PUT/PATCH /restaurants/{restaurant_id}/menu-items/{item_id}` -> Update menu item information
`POST /customers/` -> Register a customer account
`POST /customers/login` -> Sign in and receive a bearer token
`GET/PATCH/DELETE /customers/me` -> Read, update, or deactivate the authenticated customer
`GET/DELETE /customers/me/cart` -> Retrieve or clear the authenticated customer's active cart
`POST /customers/me/cart/items` -> Add an available menu item to the cart
`PATCH/DELETE /customers/me/cart/items/{item_id}` -> Change quantity or remove a cart item
`POST /customers/me/checkout` -> Revalidate and persist the cart as an order
`GET /customers/me/orders` and `GET /customers/me/orders/{order_id}` -> Retrieve owned orders

Representative data:
Restaurant records are stored in [`data/restaurants.json`](data/restaurants.json). Each record has an ID, name, cuisine, description, and rating.
Restaurant and menu-item create/update operations are persisted to the corresponding JSON files in `data/`.
Customer accounts, active carts, and order snapshots are stored in `data/customers.json`, `data/carts.json`, and `data/orders.json`. Customer workflow endpoints other than registration and sign-in require `Authorization: Bearer <access_token>`. Passwords are stored as salted PBKDF2 hashes; bearer tokens expire after 12 hours and are invalidated when the application restarts.

Tests:
From the repository root, the command to run tests is:

python -m pytest

Repository structure
```text
app/
	api/routes/       (API route handlers)
	repositories/     (JSON data access)
	services/         (Restaurant operations)
	main.py           (FastAPI Entry)
	schemas.py       ( Pydantic)
data/
	restaurants.json  (Representative restaurant records)
tests/
scrum/
	team-agreement.md (Team agreement)
pyproject.toml      (Project requirements)
requirements.txt    (Pinned dependency list)
README.md
```
