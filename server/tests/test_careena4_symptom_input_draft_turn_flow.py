from fastapi.testclient import TestClient
import pytest

import careena4.api as careena4_api
from careena4.api import app
from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.turn import ExtractedCaseInput, ExtractedObservationInput


client = TestClient(app)


class _StubMedicalExtractor:
    def extract(self, *, message: str, case_topic: str | None = None, history_messages=None) -> ExtractedCaseInput:
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


def test_careena4_chat_updates_symptom_input_draft_from_extraction_claims(monkeypatch):
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
    assert draft_response.json()["symptoms"] == ["Schwindel"]


def test_careena4_chat_merges_extracted_symptoms_with_user_edited_draft(monkeypatch):
    monkeypatch.setattr(
        careena4_api,
        "turn_engine",
        TurnEngine(medical_extractor=_StubMedicalExtractor()),
    )

    session_id = _create_session()

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
