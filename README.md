# Trip Planner

A full-stack driver trip-planning assessment built with Django REST Framework and React. The application geocodes a driver's current location, pickup, and dropoff, calculates a road route, applies FMCSA-style hours-of-service rules, and renders daily ELD logs.

## Features

- Validated trip-planning API with controlled error responses
- Nominatim geocoding with caching
- OSRM route calculation with distance, duration, legs, and geometry
- Object-oriented HOS planning for the 11-hour driving, 14-hour window, 30-minute break, 10-hour restart, and 70-hour cycle rules
- Responsive React interface with route summary and printable daily logs
- OpenAPI schema, Swagger UI, and ReDoc
- Mocked provider tests so the core suite does not depend on external services

## Project Structure

```text
backend/
  core/                 Django settings and URL configuration
  trips/
    services/           Geocoding, routing, and HOS domain services
    serializers.py      API request and response contracts
    views.py            API orchestration layer
    tests.py            Focused backend tests
frontend/
  src/
    components/         Trip form, route summary, and daily logs
    hooks/              Trip-planning state and submission workflow
    services/           API client
    types/              Shared TypeScript domain types
```

## Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL

## Backend Setup

```powershell
cd backend
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

Update `.env` with the local PostgreSQL credentials before running migrations. The backend runs at `http://127.0.0.1:8000`.

## Frontend Setup

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend runs at `http://localhost:5173`. `VITE_API_BASE_URL` should point to the backend API prefix, for example `http://127.0.0.1:8000/api/v1`.

## API Endpoints

- `GET /api/v1/health/` - service health check
- `POST /api/v1/trips/plan/` - geocode, route, and plan a trip
- `GET /api/v1/schema/` - OpenAPI schema
- `GET /api/v1/docs/` - Swagger UI
- `GET /api/v1/redoc/` - ReDoc

Example request:

```json
{
  "current_location": "Chicago, IL",
  "pickup_location": "Dallas, TX",
  "dropoff_location": "Phoenix, AZ",
  "departure_at": "2026-10-05T08:00:00Z",
  "current_cycle_used": 12
}
```

## Verification

Backend checks and tests:

```powershell
cd backend
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\python.exe manage.py test trips --keepdb
```

Frontend checks:

```powershell
cd frontend
npm run lint
npm run build
```

## Architecture Notes

The view coordinates the workflow but does not contain provider or scheduling logic. Geocoding, routing, and HOS planning are isolated services with typed serializer boundaries. This makes external APIs mockable, keeps the business rules testable, and allows the React client to consume a stable response contract.

The route preview is intentionally lightweight and uses the returned geometry without adding a map-provider dependency. A production deployment could replace it with a map library while keeping the API and domain services unchanged.

## Assessment Submission Checklist

- Add the repository URL and deployed URLs to the submission
- Record the requested walkthrough video
- Include a short demo of a successful plan and a validation/provider failure
- Verify the production environment has real secrets and provider configuration
