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


def _create_session(client: TestClient) -> str:
    response = client.post("/session", json={})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert session_id
    return session_id


def test_careena4_input_draft_initially_empty(client: TestClient):
    session_id = _create_session(client)

    response = client.get(f"/input-drafts/{session_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == session_id
    assert body["symptoms"] == []
    assert body["chips"] == []


def test_careena4_input_draft_patch_cleans_and_deduplicates_labels(client: TestClient):
    session_id = _create_session(client)

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


def test_careena4_input_draft_delete_clears_labels(client: TestClient):
    session_id = _create_session(client)

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


def test_careena4_input_draft_rejects_unknown_session(client: TestClient):
    response = client.get("/input-drafts/unknown-session")

    assert response.status_code == 404


def test_careena4_input_draft_roundtrips_after_patch(client: TestClient):
    session_id = _create_session(client)

    update_response = client.patch(
        f"/input-drafts/{session_id}",
        json={"symptoms": ["Schwindel"]},
    )
    assert update_response.status_code == 200

    followup_response = client.get(f"/input-drafts/{session_id}")

    assert followup_response.status_code == 200
    assert followup_response.json()["session_id"] == session_id
    assert followup_response.json()["chips"][0]["display_label_de"] == "Schwindel"
    assert followup_response.json()["chips"][0]["status"] == "user_edited"
