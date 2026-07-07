"""Backend server using FastAPI and Uvicorn.

App assembly only: routers, CORS, logging and startup wiring. Feature logic
lives in the feature packages (auth/, profiles/, medications/, documents/,
appointments/, chat_history/, symptoms/ and chat/ for the Careena4 chat).

Notes:
- Chat handling is session-based; Careena4 sessions live in process memory.
- Authentication and account data are persisted in PostgreSQL.
- Medical profiles are stored separately from login accounts.
- Chat history is only persisted when explicitly saved via chat_history.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from appointments.router import router as appointments_router
from appointments.simulator_router import router as fhir_simulator_router
from auth.router import router as auth_router
from chat.router import router as chat_router
from chat_history.router import router as chat_history_router
from database.connection import create_db_and_tables
from documents.router import router as documents_router
from logging_config import configure_logging
from medications.router import router as medications_router
from profiles.router import router as profiles_router
from symptoms.router import router as symptoms_router

# Compatibility re-exports: tests (and external scripts) historically accessed
# the Careena4 runtime objects through the main module. The objects themselves
# live in chat.runtime / chat.service now.
from auth.security import get_optional_current_account, get_session  # noqa: F401
from chat.runtime import (  # noqa: F401
    careena4_llm_health_status,
    careena4_person_initialiser,
    careena4_services,
    careena4_session_case_profiles,
    careena4_session_profiles,
    careena4_session_store,
    careena4_session_unbound_cases,
    careena4_simulation_runner,
    careena4_turn_engine,
    refresh_llm_health_status,
)
from chat.service import (  # noqa: F401
    _recommendation_from_history,
    build_careena4_chat_response,
)

app = FastAPI()

app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(medications_router)
app.include_router(documents_router)
app.include_router(appointments_router)
app.include_router(fhir_simulator_router)
app.include_router(chat_history_router)
app.include_router(symptoms_router)
app.include_router(chat_router)

# CORS is permissive for local Flutter development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_logging()

app.state.careena4_session_store = careena4_session_store
app.state.careena4_session_profiles = careena4_session_profiles
app.state.careena4_turn_engine = careena4_turn_engine
app.state.careena4_response_builder = build_careena4_chat_response


# Editor: Ilu
def _seed_catalog() -> None:
    """Run catalog seed imports on startup. Logs a warning on failure instead of crashing."""
    try:
        from database.seed_catalog import (
            seed_assessment_criteria,
            seed_consultation_reason_criteria_links,
            seed_consultation_reasons,
        )
        r1 = seed_consultation_reasons()
        r2 = seed_assessment_criteria()
        r3 = seed_consultation_reason_criteria_links()
        print(f"Catalog seeded: reasons={r1}, criteria={r2}, links={r3}")
    except Exception as exc:
        print(f"Warning: Catalog seeding skipped ({exc})")


@app.on_event("startup")
def on_startup():
    """
    Initialize database tables on application startup.
    """
    create_db_and_tables()
    _seed_catalog()
    n = careena4_services.safety_catalog_cache.load()
    print(f"SafetyCatalogCache loaded: {n} entries")
    refresh_llm_health_status()
