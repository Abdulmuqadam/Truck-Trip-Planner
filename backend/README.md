# Spotter.ai backend

Django REST API for the driver trip planner.

## Local setup

From this directory, create or activate the project virtual environment and install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set the database values. Then run the initial checks and migrations:

```powershell
python manage.py check
python manage.py migrate
python manage.py runserver
```

The API health endpoint is available at `http://127.0.0.1:8000/api/v1/health/`.

## Structure

- `core/`: project configuration and URL routing
- `trips/`: trip-planning domain API; scheduling and route services will be added here