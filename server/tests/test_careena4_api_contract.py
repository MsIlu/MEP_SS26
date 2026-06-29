from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def clear_careena4_state():
    main.careena4_session_profiles.clear()
    main.careena4_session_store._sessions.clear()

    yield

    main.careena4_session_profiles.clear()
    main.careena4_session_store._sessions.clear()


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(main, "create_db_and_tables", lambda: None)
    monkeypatch.setattr(main, "_seed_catalog", lambda: None)
    monkeypatch.setattr(main.careena4_services.safety_catalog_cache, "load", lambda: 0)

    def override_get_session():
        yield SimpleNamespace()

    main.app.dependency_overrides[main.get_session] = override_get_session

    with TestClient(main.app) as test_client:
        yield test_client

    main.app.dependency_overrides.clear()


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
        ),
        recommendation_state=SimpleNamespace(
            recommendation_allowed=False,
        ),
    )


def test_main_boundary_keeps_chat_contract_keys(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        main.careena4_turn_engine,
        "run_turn",
        lambda _turn_input: _fake_turn_result("Antwort aus dem Test."),
    )

    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    response = client.post(
        "/chatscreen",
        json={"message": "Ich habe Bauchschmerzen.", "session_id": session_id},
    )

    payload = response.json()
    assert payload.keys() >= {
        "response",
        "response_mode",
        "red_flag",
        "trace_notes",
        "pending_followup",
        "recommendation_ready",
        "recommendation_result",
        "action",
        "severity",
        "reply_options",
    }


def test_main_boundary_exposes_fhir_export_conflict_without_case(client: TestClient):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    response = client.get(f"/fhir/export/{session_id}")

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "No extracted medical case data available for this session."
    )
