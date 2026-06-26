from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
import main
from main import (
    app,
    careena4_session_profiles,
    careena4_session_store,
    careena4_turn_engine,
    careena4_simulation_runner,
)


@pytest.fixture(autouse=True)
def clear_careena4_state():
    careena4_session_profiles.clear()
    careena4_session_store._sessions.clear()

    yield

    careena4_session_profiles.clear()
    careena4_session_store._sessions.clear()


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(main, "create_db_and_tables", lambda: None)

    with TestClient(app) as test_client:
        yield test_client


def _fake_turn_result(response_text: str = "Okay."):
    return SimpleNamespace(
        response_text=response_text,
        response_mode="ask_followup",
        trace_notes=[],
        recommendation_result=None,
        current_turn_understanding=None,
        symptom_input_draft=None,
        medical_case=None,
        conversation_state=SimpleNamespace(
            active_question=None,
            recommendation_requested=False,
        ),
        recommendation_state=None,
    )


def test_guest_session_can_be_created(client):
    response = client.post("/session", json={})

    assert response.status_code == 200
    session_id = response.json()["session_id"]

    assert session_id
    assert careena4_session_profiles[session_id] is None


def test_server_health_endpoint_reports_ok(client):
    response = client.get("/health/server")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "server": True}


def test_llm_health_endpoint_reports_ok(client, monkeypatch):
    monkeypatch.setattr(
        main.careena4_services.llm_client,
        "is_model_available",
        lambda model: True,
    )

    response = client.get("/health/llm")

    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "ok"
    assert payload["llm"] is True
    assert payload["model"] == main.careena4_services.call_model_config.default_model


def test_llm_health_endpoint_reports_unavailable(client, monkeypatch):
    monkeypatch.setattr(
        main.careena4_services.llm_client,
        "is_model_available",
        lambda model: False,
    )

    response = client.get("/health/llm")

    payload = response.json()
    assert response.status_code == 503
    assert payload["detail"]["message"] == "LLM service is not reachable."
    assert payload["detail"]["model"] == main.careena4_services.call_model_config.default_model


def test_guest_input_draft_can_be_read(client):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    response = client.get(f"/input-drafts/{session_id}")

    assert response.status_code == 200
    assert response.json()["session_id"] == session_id
    assert response.json()["symptoms"] == []
    assert response.json()["chips"] == []


def test_profile_session_requires_auth(client):
    response = client.post("/session", json={"profile_id": 1})

    assert response.status_code == 401


def test_chat_unknown_session_returns_404(client):
    response = client.post(
        "/chatscreen",
        json={
            "session_id": "unknown-session",
            "message": "Ich habe Kopfschmerzen.",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Chat session not found."


def test_guest_chat_uses_careena4_turn_engine(client, monkeypatch):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    calls = []

    def fake_run_turn(turn_input):
        calls.append(turn_input)
        return _fake_turn_result("Careena4 Antwort.")

    monkeypatch.setattr(careena4_turn_engine, "run_turn", fake_run_turn)

    response = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "Ich habe Kopfschmerzen.",
        },
    )

    assert response.status_code == 200
    assert response.json()["response"] == "Careena4 Antwort."
    assert response.json()["red_flag"] is False
    assert len(calls) == 1


def test_chat_simrun_uses_simulation_runner_shortcut(client, monkeypatch):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    def fake_run(_request):
        raise AssertionError("simulation runner should be invoked through run_simulation_command")

    def fake_run_simulation_command(*, selector, simulation_runner):
        assert selector == ""
        assert simulation_runner is careena4_simulation_runner
        return "Simulation abgeschlossen.\nStop-Grund: recommend"

    def fake_run_turn(_turn_input):
        raise AssertionError("turn engine must not receive /simrun commands")

    monkeypatch.setattr(careena4_simulation_runner, "run", fake_run)
    monkeypatch.setattr(main, "run_simulation_command", fake_run_simulation_command)
    monkeypatch.setattr(careena4_turn_engine, "run_turn", fake_run_turn)

    response = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "/simrun",
        },
    )

    assert response.status_code == 200
    assert response.json()["response"].startswith("Simulation abgeschlossen.")
    assert response.json()["red_flag"] is False


def test_profile_draft_requires_auth(client):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    careena4_session_profiles[session_id] = 1

    response = client.get(f"/input-drafts/{session_id}")

    assert response.status_code == 401
