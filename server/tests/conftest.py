# Test case references: documents/Testfaelle_Backend.md#test-infrastruktur
# Created as part of the authentication and profile management test setup.
# Provides an isolated FastAPI test app with an in-memory SQLite database.

import sys
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from careena4.core.client import LLMClient
from careena4.core.exceptions import LLMRequestError

from auth.router import router as auth_router
from auth.security import get_session
from medications.router import router as medications_router
from documents.router import router as documents_router
from appointments.router import router as appointments_router
from chat_history.router import router as chat_history_router
from profiles.router import router as profiles_router
from symptoms.router import router as symptoms_router


class _FakeCareenaSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: list[dict[str, str]] = []
        self.case_topic = None
        self.medical_case = None
        self.conversation_state = None
        self.recommendation_state = None
        self.symptom_input_draft = None
        self.last_turn_understanding = None


class _FakeSessionStore:
    def __init__(self):
        self._sessions: dict[str, _FakeCareenaSession] = {}

    def create_session(self) -> str:
        session_id = f"test-session-{len(self._sessions) + 1}"
        self._sessions[session_id] = _FakeCareenaSession(session_id)
        return session_id

    def get(self, session_id: str):
        return self._sessions.get(session_id)


class _FakeTurnEngine:
    def run_turn(self, turn_input):
        return SimpleNamespace(
            response_text="Bitte trinken Sie ausreichend und beobachten Sie den Verlauf.",
            response_mode="ask_followup",
            trace_notes=[],
            conversation_state=SimpleNamespace(
                active_question=None,
                recommendation_requested=False,
            ),
            recommendation_result=None,
            case_topic=None,
            medical_case=None,
            recommendation_state=None,
            current_turn_understanding=None,
            symptom_input_draft=None,
        )


def _fake_response_builder(result):
    return {
        "response": result.response_text,
        "response_mode": result.response_mode,
        "red_flag": False,
        "trace_notes": [],
        "pending_followup": None,
        "recommendation_requested": False,
        "recommendation_ready": False,
        "recommendation_result": None,
        "action": None,
        "severity": None,
    }


@pytest.fixture(autouse=True)
def no_real_llm_network(monkeypatch):
    """Keep the suite offline: LLMClient must never open real connections.

    The configured LiteLLM endpoint (.env) is only reachable inside the
    university network. Without this guard every TestClient startup (health
    check) and every unmocked LLM path waits for a TCP connect timeout, which
    inflates the suite from ~2 to 18+ minutes — or silently performs real
    model inferences when the endpoint IS reachable.

    All LLM consumers degrade deterministically on LLMRequestError, and tests
    that need specific LLM behavior patch the client instance or inject fakes,
    which still overrides these class-level stubs.
    """
    def _no_model_check(self, model):
        return False

    def _no_complete(self, **kwargs):
        raise LLMRequestError("Real LLM calls are disabled in the test suite")

    monkeypatch.setattr(LLMClient, "is_model_available", _no_model_check)
    monkeypatch.setattr(LLMClient, "complete", _no_complete)


@pytest.fixture(autouse=True)
def no_real_database_startup(monkeypatch):
    """Keep the suite offline, part 2: booting main.app must not touch Postgres.

    main's startup event runs create_db_and_tables(), _seed_catalog() and
    safety_catalog_cache.load() against the real engine (127.0.0.1:5433).
    When the local Docker Postgres is not running, every psycopg connect
    blocks until its timeout, so each of the ~8 test modules that start the
    real app via TestClient waits minutes per test.

    Tests exercise DB behavior through the isolated SQLite test app or their
    own fixtures; none of them rely on the startup-seeded real database.
    """
    main = sys.modules.get("main")
    if main is None:
        # No collected test imports main, so nothing can boot the real app.
        return

    monkeypatch.setattr(main, "create_db_and_tables", lambda: None)
    monkeypatch.setattr(main, "_seed_catalog", lambda: None)
    monkeypatch.setattr(main.careena4_services.safety_catalog_cache, "load", lambda: 0)


@pytest.fixture()
def db_session():
    """
    Create a fresh in-memory database session for each test.

    StaticPool keeps the same in-memory SQLite database available across
    all connections used during a single test.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    """
    Create a FastAPI test client with auth and profile routers.

    The production database dependency is overridden so tests never touch
    the real PostgreSQL database.
    """
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(profiles_router)
    app.include_router(medications_router)
    app.include_router(documents_router)
    app.include_router(appointments_router)
    app.include_router(chat_history_router)
    app.include_router(symptoms_router)

    app.state.careena4_session_store = _FakeSessionStore()
    app.state.careena4_session_profiles = {}
    app.state.careena4_turn_engine = _FakeTurnEngine()
    app.state.careena4_response_builder = _fake_response_builder

    def get_test_session():
        yield db_session

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
