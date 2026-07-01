import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient

import main
from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.turn import ExtractedCaseInput, ExtractedObservationInput


@pytest.fixture(autouse=True)
def clear_sessions():
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


class _StubMedicalExtractor:
    def extract(self, *, message: str, history_messages=None) -> ExtractedCaseInput:
        return ExtractedCaseInput(
            observations=[
                ExtractedObservationInput(
                    type="symptom",
                    normalized_label_de="Schwindel",
                    status="active",
                )
            ]
        )


def _create_session(client: TestClient) -> str:
    response = client.post("/session", json={})
    assert response.status_code == 200
    return response.json()["session_id"]


def test_careena4_chat_updates_symptom_input_draft_from_extraction_claims(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        main,
        "careena4_turn_engine",
        TurnEngine(medical_extractor=_StubMedicalExtractor()),
    )

    session_id = _create_session(client)

    chat_response = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "Ich habe Schwindel.",
        },
    )

    assert chat_response.status_code == 200

    draft_response = client.get(f"/input-drafts/{session_id}")

    assert draft_response.status_code == 200
    assert draft_response.json()["symptoms"] == ["Schwindel"]


def test_careena4_chat_merges_extracted_symptoms_with_user_edited_draft(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        main,
        "careena4_turn_engine",
        TurnEngine(medical_extractor=_StubMedicalExtractor()),
    )

    session_id = _create_session(client)

    patch_response = client.patch(
        f"/input-drafts/{session_id}",
        json={"symptoms": ["Kopfschmerzen"]},
    )
    assert patch_response.status_code == 200

    chat_response = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "Ich habe Schwindel.",
        },
    )

    assert chat_response.status_code == 200

    draft_response = client.get(f"/input-drafts/{session_id}")

    assert draft_response.status_code == 200
    assert draft_response.json()["symptoms"] == ["Kopfschmerzen", "Schwindel"]
