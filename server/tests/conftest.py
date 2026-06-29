# Test case references: documents/Testfaelle_Backend.md#test-infrastruktur
# Created as part of the authentication and profile management test setup.
# Provides an isolated FastAPI test app with an in-memory SQLite database.

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from auth.router import router as auth_router
from auth.security import get_session
from medications.router import router as medications_router
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
