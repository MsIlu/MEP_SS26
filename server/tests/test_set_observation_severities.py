"""Tests for POST /chatscreen/set-severities.

Covers the full flow:
  1. Severity is written into the session MedicalCase.
  2. A pending active_question of kind 'severity' for the same observation
     is cleared so the backend will not ask again.
  3. Unrelated active questions are left untouched.
  4. Missing session → 404.
  5. No MedicalCase yet → graceful no-op (200).
"""

import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient

import main
from main import app, careena4_session_store, careena4_session_profiles
from careena4.infrastructure.session_store import Careena4Session
from careena4.models.domain.case import MedicalCase
from careena4.models.domain.dialogue import ActiveQuestion, ConversationState
from careena4.models.domain.observation import Observation


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_state():
    careena4_session_profiles.clear()
    careena4_session_store._sessions.clear()
    yield
    careena4_session_profiles.clear()
    careena4_session_store._sessions.clear()


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(main, "create_db_and_tables", lambda: None)

    def override_get_session():
        yield SimpleNamespace()

    app.dependency_overrides[main.get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _make_session(*, with_case: bool = True) -> tuple[str, Careena4Session]:
    """Create a session in the store and return (session_id, session)."""
    session_id = careena4_session_store.create_session()
    session = careena4_session_store.get(session_id)
    if with_case:
        session.medical_case = MedicalCase()
    return session_id, session


def _add_observation(session: Careena4Session, label: str, severity: str | None = None) -> Observation:
    obs = Observation(type="symptom", label=label, severity=severity)
    session.medical_case.observations.append(obs)
    return obs


def _set_pending_severity_question(session: Careena4Session, observation_id: str) -> None:
    session.conversation_state.active_question = ActiveQuestion(
        kind="followup",
        question_intent="severity",
        target_observation_id=observation_id,
        prompt_text="Auf einer Skala von 1 bis 10 — wie stark sind die Beschwerden?",
    )


# ---------------------------------------------------------------------------
# Tests: basic severity update
# ---------------------------------------------------------------------------

def test_set_severities_updates_matching_observation(client):
    session_id, session = _make_session()
    _add_observation(session, "Kopfschmerzen")

    response = client.post("/chatscreen/set-severities", json={
        "session_id": session_id,
        "severities": {"Kopfschmerzen": 3},
    })

    assert response.status_code == 200
    obs = session.medical_case.observations[0]
    assert obs.severity == "3"


def test_set_severities_is_case_insensitive(client):
    session_id, session = _make_session()
    _add_observation(session, "Halsschmerzen")

    client.post("/chatscreen/set-severities", json={
        "session_id": session_id,
        "severities": {"halsschmerzen": 7},
    })

    assert session.medical_case.observations[0].severity == "7"


def test_set_severities_updates_multiple_observations(client):
    session_id, session = _make_session()
    _add_observation(session, "Kopfschmerzen")
    _add_observation(session, "Halsschmerzen")

    client.post("/chatscreen/set-severities", json={
        "session_id": session_id,
        "severities": {"Kopfschmerzen": 3, "Halsschmerzen": 2},
    })

    severities = {obs.label: obs.severity for obs in session.medical_case.observations}
    assert severities == {"Kopfschmerzen": "3", "Halsschmerzen": "2"}


def test_set_severities_ignores_inactive_observations(client):
    session_id, session = _make_session()
    obs = _add_observation(session, "Kopfschmerzen")
    obs.status = "negated"  # not in is_active() set

    client.post("/chatscreen/set-severities", json={
        "session_id": session_id,
        "severities": {"Kopfschmerzen": 5},
    })

    assert obs.severity is None  # not updated


# ---------------------------------------------------------------------------
# Tests: active_question clearing
# ---------------------------------------------------------------------------

def test_set_severities_clears_pending_severity_question(client):
    session_id, session = _make_session()
    obs = _add_observation(session, "Kopfschmerzen")
    _set_pending_severity_question(session, obs.observation_id)

    assert session.conversation_state.active_question is not None

    client.post("/chatscreen/set-severities", json={
        "session_id": session_id,
        "severities": {"Kopfschmerzen": 3},
    })

    assert session.conversation_state.active_question is None


def test_set_severities_does_not_clear_question_for_different_observation(client):
    """Question for obs B must not be cleared when only obs A's severity is set."""
    session_id, session = _make_session()
    obs_a = _add_observation(session, "Kopfschmerzen")
    obs_b = _add_observation(session, "Halsschmerzen")
    _set_pending_severity_question(session, obs_b.observation_id)

    client.post("/chatscreen/set-severities", json={
        "session_id": session_id,
        "severities": {"Kopfschmerzen": 3},  # only A
    })

    # Question is for B — should still be there
    assert session.conversation_state.active_question is not None
    assert session.conversation_state.active_question.target_observation_id == obs_b.observation_id


def test_set_severities_does_not_clear_non_severity_question(client):
    """A pending question with a different intent must be left untouched."""
    session_id, session = _make_session()
    obs = _add_observation(session, "Kopfschmerzen")
    session.conversation_state.active_question = ActiveQuestion(
        kind="followup",
        question_intent="duration",
        target_observation_id=obs.observation_id,
        prompt_text="Seit wann haben Sie die Beschwerden?",
    )

    client.post("/chatscreen/set-severities", json={
        "session_id": session_id,
        "severities": {"Kopfschmerzen": 3},
    })

    assert session.conversation_state.active_question is not None
    assert session.conversation_state.active_question.question_intent == "duration"


# ---------------------------------------------------------------------------
# Tests: edge cases
# ---------------------------------------------------------------------------

def test_set_severities_returns_404_for_unknown_session(client):
    response = client.post("/chatscreen/set-severities", json={
        "session_id": "does-not-exist",
        "severities": {"Kopfschmerzen": 3},
    })

    assert response.status_code == 404


def test_set_severities_is_noop_when_no_medical_case(client):
    session_id, _ = _make_session(with_case=False)

    response = client.post("/chatscreen/set-severities", json={
        "session_id": session_id,
        "severities": {"Kopfschmerzen": 3},
    })

    assert response.status_code == 200
    assert response.json() == {"ok": True}
