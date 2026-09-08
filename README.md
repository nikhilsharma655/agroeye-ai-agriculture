# 🌾 AgroEye — AI-Powered Smart Agriculture Platform

AgroEye is a full-stack digital agricultural assistant. Farmers enter data
about their farm, soil, and environment, and AgroEye uses real trained
Scikit-learn models plus backend-computed agronomic logic to recommend what
to grow, how much to fertilize and irrigate, and what disease risks to watch
for — all surfaced through a clean, farmer-friendly React dashboard.

## Features

- **AI Crop Recommendation** — Random-Forest classifier trained on soil/climate profiles for 15 crops, returns top-5 ranked suggestions with confidence scores.
- **Crop Yield Prediction** — Gradient-Boosting regressor estimating yield per hectare and total harvest, with a confidence range.
- **Fertilizer Recommendation** — Backend-computed N-P-K deficit analysis against crop-specific targets, growth-stage aware.
- **Disease Risk Prediction** — Structured-data classifier (temperature/humidity/rainfall/soil moisture/history) predicting low/medium/high risk. `POST /api/disease/predict-image` already exists as the integration point for an image-based CNN (`ml/inference/disease_image_infer.py`) — it currently returns a clear `501 IMAGE_MODEL_NOT_AVAILABLE` with instructions, since no image model is trained/bundled, but no route or service code will need to change once one is added.
- **Irrigation Recommendation** — Backend water-balance calculation (never hardcoded in the frontend) factoring in soil moisture deficit, evapotranspiration proxies, and recent rainfall.
- **Farm Management** — Full CRUD for farms and crops, historical soil/weather tracking, and one-click **live weather refresh** (Open-Meteo — no API key needed) that geocodes the farm's location and pulls current temperature/humidity/rainfall.
- **AI Insights Dashboard** — Consolidated, farmer-friendly insights across soil, crop, irrigation, yield, disease, and fertilizer.
- **Analytics** — Historical prediction trends per farm.
- **n8n Automation** — Webhook-driven alerts (high disease risk, low soil moisture), a daily scheduled farm summary, and recommendation-created notifications — fully decoupled so n8n can be swapped for another automation engine.
- **Auth** — JWT-based registration/login, bcrypt password hashing, protected routes.

## Architecture

```
React.js (Vite + Tailwind + React Router + Axios)
            │  REST (JSON)
            ▼
FastAPI REST API  ──►  Service Layer (business logic)
            │                   │
            │                   ├──► ml/ package (Scikit-learn inference)
            │                   ├──► fertilizer_service / irrigation_service (agronomic formulas)
            │                   └──► n8n_service (outbound webhooks)
            ▼
     PostgreSQL (SQLAlchemy models)

AgroEye (FastAPI) ──webhook──► n8n ──► Email / SMS / Notifications
AgroEye (FastAPI) ◄──webhook── n8n   (daily summary pull, acks)
```

Everything ML-related lives in `ml/`, completely independent of FastAPI —
`backend/app/services/ml_service.py` is the only bridge. This means models
can be retrained, swapped, or extended (e.g. add a CNN for image-based
disease detection, plug in live weather/IoT/satellite feeds) without
touching route or business logic code.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, React Router, Axios, Tailwind CSS, Recharts, lucide-react |
| Backend | FastAPI, Pydantic, Uvicorn, python-jose (JWT), passlib (bcrypt) |
| ML | Scikit-learn, Pandas, NumPy, Joblib |
| Database | PostgreSQL (SQLAlchemy ORM); SQLite supported for local dev |
| Automation | n8n (webhook-based) |
| Containerization | Docker, docker-compose |

## Project Structure

```
agroeye/
├── backend/            FastAPI app (routes, services, models, schemas, auth)
├── ml/                 Datasets, preprocessing, training, evaluation, inference, saved_models
├── frontend/            React app (pages, components, context, services)
├── n8n/                 Importable n8n workflow JSON + integration README
├── data/                Reserved for future raw/external data sources
├── docs/                Reserved for extended documentation
├── docker-compose.yml
└── README.md
```

## Getting Started

### 1. Train the ML models

```bash
cd ml
pip install -r ../backend/requirements.txt   # scikit-learn, pandas, numpy, joblib, etc.
python training/train_models.py              # generates datasets + trains + evaluates + saves via Joblib
python evaluation/generate_report.py         # prints a consolidated evaluation report
```

This populates `ml/saved_models/` with the trained `.pkl` models, scalers,
and metadata JSON files that the backend loads at import time. **Models are
trained once, offline — never retrained on request.**

### 2. Backend setup

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# For local dev without Postgres, set DATABASE_URL=sqlite:///./agroeye.db in .env
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs (Swagger) · http://localhost:8000/redoc

### 3. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_BASE_URL
npm run dev
```

App: http://localhost:5173

### 4. Database

- **Production**: PostgreSQL via `DATABASE_URL=postgresql://user:pass@host:5432/db`.
- **Local dev**: SQLite via `DATABASE_URL=sqlite:///./agroeye.db`.
- **Schema migrations**: managed with Alembic (`backend/alembic/`). The Docker
  entrypoint runs `alembic upgrade head` automatically before starting the
  server. For local development:
  ```bash
  cd backend
  alembic upgrade head                              # apply migrations
  alembic revision --autogenerate -m "add X column"  # generate a new one after changing models
  alembic downgrade -1                               # roll back one revision
  ```
  `app.database.init_db()` (a `create_all()` call) still runs on every app
  startup as a zero-config convenience for local dev and the test suite — it
  only adds missing tables and never alters existing ones, so it's safe
  alongside Alembic-managed environments.

### 5. n8n setup

See [`n8n/README.md`](n8n/README.md) for full instructions on importing the
four workflows (disease alert, irrigation alert, daily summary, new
recommendation notification) and wiring their webhook URLs into the backend
`.env`.

### 6. Testing

Backend:
```bash
cd backend
pytest -v
```

Covers authentication, farm CRUD, all ML-backed endpoints, the live weather
integration (mocked), the image-detection scaffold's graceful failure, and
webhook signature verification — 26 tests.

Frontend:
```bash
cd frontend
npm test          # runs once (vitest run)
npm run test:watch
```

Covers reusable components (`Loader`, `ErrorState`, `EmptyState`,
`SeverityBadge`, `PageHeader`, `StatCard`, `FarmPicker`) and page-level
behavior (`Login` success/failure/navigation, `CropRecommendation` form
submission and error handling) using Vitest + React Testing Library, with
the API layer mocked — 29 tests.

### 7. Docker (full stack)

```bash
cp .env.example .env   # set JWT_SECRET_KEY and N8N_WEBHOOK_SHARED_SECRET
docker compose up --build
```

This brings up PostgreSQL, the FastAPI backend, the React frontend (served
via Nginx), and n8n — all networked together. Train the ML models locally
first (step 1) since `ml/saved_models/` is mounted into the backend
container.

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API / Docs | http://localhost:8000/docs |
| n8n | http://localhost:5678 |
| PostgreSQL | localhost:5432 |

## API Overview

All endpoints return a consistent envelope:

```json
{ "success": true, "message": "...", "data": { ... } }
{ "success": false, "message": "...", "error": "VALIDATION_ERROR" }
```

Key route groups: `/api/auth`, `/api/users`, `/api/farms` (including
`/api/farms/{id}/weather/refresh` for live weather), `/api/crops`,
`/api/recommendations`, `/api/yield`, `/api/fertilizer`, `/api/disease`
(including the image-detection scaffold at `/api/disease/predict-image`),
`/api/irrigation`, `/api/insights`, `/api/analytics`, `/api/webhooks`,
`/api/notifications`. Full request/response schemas are in Swagger at `/docs`.

## ML Model Evaluation Summary

Each model is trained against multiple candidate algorithms and the
best-performing one (by weighted F1 for classifiers, R² for regressors) is
selected automatically and serialized — see `ml/evaluation/generate_report.py`
output for exact numbers on your trained run. On the bundled synthetic
dataset:

- **Crop recommendation**: Random Forest selected, ~98% F1 across 15 crops.
- **Yield prediction**: Gradient Boosting selected, R² ≈ 0.99.
- **Disease risk**: Gradient Boosting selected, ~80% accuracy (appropriately
  modest — structured environmental data is an inherently noisier proxy for
  disease than lab diagnostics or imagery).

## Security Notes

- Passwords hashed with bcrypt; JWTs signed with `JWT_SECRET_KEY` (must be
  overridden in production).
- All secrets are environment-variable driven — see `.env.example` files at
  the root, `backend/`, and `frontend/`. Nothing is hardcoded or committed.
- n8n webhooks (both directions) are protected by a shared-secret header
  (`X-AgroEye-Signature`).
- CORS origins are explicitly configured, not wildcarded, in production.

## Future Improvements

- Train and wire in the image-based CNN disease detection model — the
  scaffold (`ml/inference/disease_image_infer.py`) and API endpoint
  (`POST /api/disease/predict-image`) already exist; only the model itself
  is missing (see that module's docstring for the exact steps).
- Extend live weather beyond current conditions to short-range forecasts
  (Open-Meteo supports this) to feed forward-looking irrigation planning.
- Integrate IoT soil sensors to replace manually entered soil readings, the
  same way live weather now replaces manually entered climate readings.
- Add satellite imagery (NDVI) for remote crop health monitoring.
- Mobile app (React Native) reusing the same FastAPI backend.
- Role-based access for agronomists/cooperatives managing multiple farmers.
