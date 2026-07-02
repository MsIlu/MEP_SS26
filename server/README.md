# Careena FastAPI Backend

This directory contains the FastAPI backend for Careena.

## Responsibilities

- authentication, accounts, and profile access control
- medication, symptom diary, document, appointment, and chat-history APIs
- Careena4 chat orchestration, safety checks, symptom drafts, and recommendations
- FHIR bundle creation and local HAPI-FHIR appointment adapter integration

Medical safety decisions are handled in the backend. The Flutter app displays
the resulting chat responses, warning state, and recommendations.

## Required Environment

Create `.env` in the repository root or export these variables before running:

```env
DATABASE_URL=postgresql+psycopg://mep_user:mep_password@127.0.0.1:5433/mep_server
SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_VALUE
LITELLM_BASE_URL=YOUR_LITELLM_URL
LITELLM_API_KEY=YOUR_LITELLM_KEY
LITELLM_MODEL=medgemma:27b
SQL_ECHO=false
```

`DATABASE_URL` may point to SQLite for tests, but production/demo startup uses
PostgreSQL through `docker-compose.yml`.

## Local Run

From the repository root:

```bash
docker compose up -d postgres fhir-server
```

Then from `server`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
SECRET_KEY=test-secret-key \
DATABASE_URL=postgresql+psycopg://mep_user:mep_password@127.0.0.1:5433/mep_server \
LITELLM_BASE_URL=YOUR_LITELLM_URL \
LITELLM_API_KEY=YOUR_LITELLM_KEY \
LITELLM_MODEL=medgemma:27b \
.venv/bin/python -m uvicorn main:app --reload
```

Useful endpoints:

- `GET /health/server`
- `GET /health/llm`
- `GET /docs`
- `POST /session`
- `POST /chatscreen`
- `POST /appointments/search`

## Tests

The test suite runs without PostgreSQL or real LLM credentials:

```bash
SECRET_KEY=test-secret-key \
DATABASE_URL=sqlite:// \
LITELLM_BASE_URL=dummy \
LITELLM_API_KEY=dummy \
LITELLM_MODEL=dummy \
.venv/bin/python -m pytest tests -q
```

The backend test matrix is documented in
`../documents/testing/Testfaelle_Backend.md`.

## Notes

Startup creates SQLModel tables and runs PostgreSQL-only legacy migrations only
when the active SQLAlchemy dialect is PostgreSQL. This keeps SQLite test startup
portable while preserving the local demo migration path.
