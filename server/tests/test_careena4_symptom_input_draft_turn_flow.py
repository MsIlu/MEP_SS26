from fastapi.testclient import TestClient

from careena4.api import app


client = TestClient(app)


def _create_session() -> str:
    response = client.post("/session")
    assert response.status_code == 200
    return response.json()["session_id"]


def test_careena4_chat_updates_symptom_input_draft_from_extraction_claims():
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


def test_careena4_chat_merges_extracted_symptoms_with_user_edited_draft():
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
