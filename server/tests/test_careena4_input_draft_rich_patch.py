
from fastapi.testclient import TestClient

from careena4.api import app


client = TestClient(app)


def _create_session() -> str:
    response = client.post("/session")
    assert response.status_code == 200
    return response.json()["session_id"]


def test_input_draft_patch_accepts_rich_chips_and_preserves_candidate_mapping():
    session_id = _create_session()

    response = client.patch(
        f"/input-drafts/{session_id}",
        json={
            "chips": [
                {
                    "display_label_de": "Schwindel",
                    "normalized_label_de": "schwindel",
                    "clinical_term_de": "Vertigo / Schwindel",
                    "mapping_confidence": 0.92,
                    "status": "user_confirmed",
                    "source": "careena4_extraction",
                    "mapping": {
                        "raw_text": "Schwindel",
                        "lay_term_de": "Schwindel",
                        "clinical_term_de": "Vertigo / Schwindel",
                        "confidence": 0.92,
                        "mapper_name": "local_symptom_mapping",
                        "validation_status": "mapping_candidate",
                    },
                }
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["symptoms"] == ["Schwindel"]
    assert len(body["chips"]) == 1

    chip = body["chips"][0]
    assert chip["display_label_de"] == "Schwindel"
    assert chip["status"] == "user_confirmed"
    assert chip["mapping_confidence"] == 0.92
    assert chip["mapping"]["validation_status"] == "mapping_candidate"


def test_input_draft_patch_clears_stale_mapping_for_user_edited_chip():
    session_id = _create_session()

    response = client.patch(
        f"/input-drafts/{session_id}",
        json={
            "chips": [
                {
                    "display_label_de": "Neu beschriebenes Symptom",
                    "clinical_term_de": "Old stale term",
                    "mapping_confidence": 0.99,
                    "status": "user_edited",
                    "source": "careena4_extraction",
                    "mapping": {
                        "raw_text": "old",
                        "lay_term_de": "old",
                        "clinical_term_de": "Old stale term",
                        "confidence": 0.99,
                        "mapper_name": "old_mapper",
                        "validation_status": "mapping_candidate",
                    },
                }
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["symptoms"] == ["Neu beschriebenes Symptom"]
    chip = body["chips"][0]
    assert chip["display_label_de"] == "Neu beschriebenes Symptom"
    assert chip["status"] == "user_edited"
    assert chip["source"] == "user"
    assert chip["clinical_term_de"] is None
    assert chip["mapping_confidence"] is None
    assert chip["mapping"] is None


def test_input_draft_patch_still_supports_legacy_symptoms_body():
    session_id = _create_session()

    response = client.patch(
        f"/input-drafts/{session_id}",
        json={"symptoms": ["Schwindel"]},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["symptoms"] == ["Schwindel"]
    assert body["chips"][0]["display_label_de"] == "Schwindel"
    assert body["chips"][0]["status"] == "user_edited"
    assert body["chips"][0]["source"] == "user"
    