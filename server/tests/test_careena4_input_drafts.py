from fastapi.testclient import TestClient

from careena4.api import app


client = TestClient(app)


def _create_session() -> str:
    response = client.post("/session")
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id
    return session_id


def test_careena4_input_draft_initially_empty():
    session_id = _create_session()

    response = client.get(f"/input-drafts/{session_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == session_id
    assert body["symptoms"] == []
    assert body["chips"] == []


def test_careena4_input_draft_patch_cleans_and_deduplicates_labels():
    session_id = _create_session()

    response = client.patch(
        f"/input-drafts/{session_id}",
        json={"symptoms": [" Bauchschmerzen ", "", "Schmerzen", "Bauchschmerzen"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == session_id
    assert body["symptoms"] == ["Bauchschmerzen"]
    assert [chip["display_label_de"] for chip in body["chips"]] == ["Bauchschmerzen"]
    assert body["chips"][0]["status"] == "user_edited"
    assert body["chips"][0]["source"] == "user"

    get_response = client.get(f"/input-drafts/{session_id}")
    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["session_id"] == session_id
    assert get_body["symptoms"] == ["Bauchschmerzen"]
    assert [chip["display_label_de"] for chip in get_body["chips"]] == ["Bauchschmerzen"]


def test_careena4_input_draft_delete_clears_labels():
    session_id = _create_session()

    patch_response = client.patch(
        f"/input-drafts/{session_id}",
        json={"symptoms": ["Kopfschmerzen", "Uebelkeit"]},
    )
    assert patch_response.status_code == 200

    delete_response = client.delete(f"/input-drafts/{session_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": "Draft cancelled successfully.",
        "session_id": session_id,
    }

    get_response = client.get(f"/input-drafts/{session_id}")
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["session_id"] == session_id
    assert body["symptoms"] == []
    assert body["chips"] == []


def test_careena4_input_draft_rejects_unknown_session():
    response = client.get("/input-drafts/unknown-session")

    assert response.status_code == 404


def test_careena4_case_debug_response_contains_symptom_input_draft():
    session_id = _create_session()

    update_response = client.patch(
        f"/input-drafts/{session_id}",
        json={"symptoms": ["Schwindel"]},
    )
    assert update_response.status_code == 200

    case_response = client.get(f"/case/{session_id}")

    assert case_response.status_code == 200
    assert case_response.json()["symptom_input_draft"]["session_id"] == session_id
    assert case_response.json()["symptom_input_draft"]["chips"][0]["display_label_de"] == "Schwindel"
    assert case_response.json()["symptom_input_draft"]["chips"][0]["status"] == "user_edited"
