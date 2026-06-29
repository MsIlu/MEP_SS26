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
    def extract(self, *, message: str, topic_context: str | None = None, history_messages=None) -> ExtractedCaseInput:
        return ExtractedCaseInput(
            observations=[
                ExtractedObservationInput(
                    type="symptom",
                    label="Schwindel",
                    status="active",
                )
            ]
        )


def _create_session(client: TestClient) -> str:
    response = client.post("/session", json={})
    assert response.status_code == 200
    return response.json()["session_id"]


def test_input_draft_response_exposes_legacy_symptoms_and_rich_chips(
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
    body = draft_response.json()

    assert body["session_id"] == session_id
    assert body["symptoms"] == ["Schwindel"]

    assert len(body["chips"]) == 1
    chip = body["chips"][0]
    assert chip["display_label_de"] == "Schwindel"
    assert chip["status"] == "extracted"
    assert chip["source"] == "careena4_extraction"

    assert chip["mapping_confidence"] == 0.92
    assert chip["mapping"]["validation_status"] == "mapping_candidate"


def test_input_draft_patch_still_accepts_legacy_symptom_list(client: TestClient):
    session_id = _create_session(client)

    patch_response = client.patch(
        f"/input-drafts/{session_id}",
        json={"symptoms": ["Kopfschmerzen"]},
    )

    assert patch_response.status_code == 200
    body = patch_response.json()

    assert body["symptoms"] == ["Kopfschmerzen"]
    assert len(body["chips"]) == 1
    assert body["chips"][0]["display_label_de"] == "Kopfschmerzen"
    assert body["chips"][0]["status"] == "user_edited"
    assert body["chips"][0]["source"] == "user"
