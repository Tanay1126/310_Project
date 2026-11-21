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

## API contract

The generated OpenAPI 3 contract is available at [`/openapi.json`](http://127.0.0.1:8000/openapi.json).
It includes request/response models, validation constraints, status codes, and the `BearerAuth`
HTTP bearer security scheme. Swagger UI is available at [`/docs`](http://127.0.0.1:8000/docs).

### Base and restaurant endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Serve the frontend |
| `GET` | `/health/` | Application health check |
| `GET` | `/restaurants/health` | Restaurant API health check |
| `GET` | `/restaurants/` | Search by `q`, `cuisine`, `min_rating`, or `max_rating` |
| `POST` | `/restaurants/` | Create a restaurant |
| `GET` | `/restaurants/{id}` | Get a restaurant |
| `PUT`, `PATCH` | `/restaurants/{id}` | Replace or update a restaurant |
| `GET` | `/restaurants/{id}/menus` | List menus for a restaurant |
| `GET` | `/restaurants/{restaurant_id}/menus/{menu_id}` | Get a menu |
| `GET` | `/restaurants/{restaurant_id}/menus/{menu_id}/items` | List menu items on a menu |
| `GET` | `/restaurants/{restaurant_id}/menu-items` | List all items for a restaurant |
| `POST` | `/restaurants/{restaurant_id}/menu-items` | Add a menu item; requires `category_id` |
| `GET` | `/restaurants/{restaurant_id}/menu-items/{item_id}` | Get a menu item |
| `PUT`, `PATCH` | `/restaurants/{restaurant_id}/menu-items/{item_id}` | Replace or update a menu item |

### Customer, cart, and order endpoints

| Method | Path | Authentication | Purpose |
|---|---|---|---|
| `POST` | `/customers/` | None | Register a customer; returns `201` |
| `POST` | `/customers/login` | None | Validate credentials and return an access token |
| `GET` | `/customers/me` | Bearer | Get the signed-in customer |
| `PATCH` | `/customers/me` | Bearer | Update supplied profile fields |
| `DELETE` | `/customers/me` | Bearer | Deactivate the signed-in customer; returns `204` |
| `GET` | `/customers/me/cart` | Bearer | Get or create the active cart |
| `POST` | `/customers/me/cart/items` | Bearer | Add an available item with a quantity from 1 to 99 |
| `PATCH` | `/customers/me/cart/items/{item_id}` | Bearer | Set a cart item's quantity |
| `DELETE` | `/customers/me/cart/items/{item_id}` | Bearer | Remove a cart item |
| `DELETE` | `/customers/me/cart` | Bearer | Clear the cart |
| `POST` | `/customers/me/checkout` | Bearer | Revalidate and persist the cart as an order; returns `201` |
| `GET` | `/customers/me/orders` | Bearer | List orders owned by the customer |
| `GET` | `/customers/me/orders/{order_id}` | Bearer | Get one owned order |

### Authentication

Register and sign in, then send the returned token in subsequent requests:

```powershell
$session = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/customers/login" `
  -ContentType "application/json" `
  -Body '{"email":"customer@example.com","password":"CorrectHorse123"}'

$headers = @{ Authorization = "Bearer $($session.access_token)" }
Invoke-RestMethod -Uri "http://127.0.0.1:8000/customers/me/cart" -Headers $headers
```

Access tokens expire after 12 hours and are invalidated when the application restarts.

### Response and error conventions

- Successful creates use `201 Created`; successful customer deactivation uses `204 No Content`.
- `400`/`404` responses are used for missing or invalid resource relationships, `401` for missing or invalid authentication, `409` for workflow/state conflicts, `422` for Pydantic input validation, and `204` for no-content success.
- Error responses use FastAPI's JSON format: `{"detail": "message"}`.
- Checkout and cart reads use current menu prices and availability. Checkout stores an order snapshot and clears the cart only after successful persistence.

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
