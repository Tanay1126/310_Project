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


Run the application
From the repository root, with the virtual environment active:

python -m uvicorn app.main:app --reload


The API is available at `http://127.0.0.1:8000`. Interactive Swagger documentation is at [`/docs`](http://127.0.0.1:8000/docs).

API endpoints
`GET/`-> Health 
`GET/restaurants/` -> List restaurants 
 `GET/restaurants/{restaurant_id}` -> Get a restaurant by ID; returns 404 if it does not exist 

Representative data
Restaurant records are stored in [`data/restaurants.json`](data/restaurants.json). Each record has an ID, name, cuisine, description, and rating.

Tests

The command to run tests is

pytest

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
scrum/
	team-agreement.md Team agreement
pyproject.toml      (Project requirements)
requirements.txt    (Pinned dependency list)
```