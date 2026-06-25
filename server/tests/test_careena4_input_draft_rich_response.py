from fastapi.testclient import TestClient
import pytest

import careena4.api as careena4_api
from careena4.api import app
from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.turn import ExtractedCaseInput, ExtractedObservationInput


client = TestClient(app)


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


@pytest.fixture(autouse=True)
def clear_sessions():
    careena4_api.session_store._sessions.clear()
    yield
    careena4_api.session_store._sessions.clear()


def _create_session() -> str:
    response = client.post("/session")
    assert response.status_code == 200
    return response.json()["session_id"]


def test_input_draft_response_exposes_legacy_symptoms_and_rich_chips(monkeypatch):
    monkeypatch.setattr(
        careena4_api,
        "turn_engine",
        TurnEngine(medical_extractor=_StubMedicalExtractor()),
    )

    session_id = _create_session()

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

    # Mapping fields remain candidates. They are not validated case truth.
    assert chip["snomed_code"] == "404640003"
    assert chip["mapping_confidence"] == 0.92
    assert chip["mapping"]["validation_status"] == "mapping_candidate"


def test_input_draft_patch_still_accepts_legacy_symptom_list():
    session_id = _create_session()

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
