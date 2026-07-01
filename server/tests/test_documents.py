"""Tests document creation, listing, updates, access protection, and deletion."""

import base64

from sqlmodel import select

from database.models import DocumentEntry

VALID_PDF_BYTES = b"%PDF-1.4\n%Careena test document\n%%EOF"
VALID_PDF_BASE64 = base64.b64encode(VALID_PDF_BYTES).decode("ascii")


def register_user(client, email="document@example.com"):
    """Register a user and return token, headers and initial profile id."""
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "12345678",
            "display_name": "Anna",
            "date_of_birth": "2000-04-12",
            "biological_sex": "female",
        },
    )

    assert response.status_code == 200

    data = response.json()

    return {
        "token": data["access_token"],
        "profile_id": data["profiles"][0]["id"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
    }


def create_document(client, auth, **overrides):
    """Create a document entry for the registered user's initial profile."""
    payload = {
        "name": "Befund.pdf",
        "category": "findings",
        "source": "uploaded",
        "size_in_bytes": len(VALID_PDF_BYTES),
        "mime_type": "application/pdf",
        "file_data_base64": VALID_PDF_BASE64,
        "created_at": "2026-06-23T10:00:00",
    }
    payload.update(overrides)

    return client.post(
        f"/profiles/{auth['profile_id']}/documents",
        headers=auth["headers"],
        json=payload,
    )


def test_create_document_persists_profile_scoped_entry(client, db_session):
    auth = register_user(client)

    response = create_document(client, auth)

    assert response.status_code == 200

    data = response.json()
    assert data["profile_id"] == auth["profile_id"]
    assert data["name"] == "Befund.pdf"
    assert data["category"] == "findings"
    assert data["source"] == "uploaded"
    assert data["size_in_bytes"] == len(VALID_PDF_BYTES)
    assert data["mime_type"] == "application/pdf"
    assert data["file_data_base64"] == VALID_PDF_BASE64

    entry = db_session.get(DocumentEntry, data["id"])
    assert entry is not None
    assert entry.profile_id == auth["profile_id"]


def test_list_documents_returns_newest_first(client):
    auth = register_user(client)

    old_response = create_document(
        client,
        auth,
        name="Alter Befund.pdf",
        created_at="2026-06-20T10:00:00",
    )
    new_response = create_document(
        client,
        auth,
        name="Neuer Befund.pdf",
        created_at="2026-06-24T10:00:00",
    )

    assert old_response.status_code == 200
    assert new_response.status_code == 200

    response = client.get(
        f"/profiles/{auth['profile_id']}/documents",
        headers=auth["headers"],
    )

    assert response.status_code == 200
    assert [entry["name"] for entry in response.json()] == [
        "Neuer Befund.pdf",
        "Alter Befund.pdf",
    ]
    assert "file_data_base64" not in response.json()[0]


def test_get_document_returns_file_data(client):
    auth = register_user(client)
    create_response = create_document(client, auth)
    document_id = create_response.json()["id"]

    response = client.get(
        f"/profiles/{auth['profile_id']}/documents/{document_id}",
        headers=auth["headers"],
    )

    assert response.status_code == 200
    assert response.json()["file_data_base64"] == VALID_PDF_BASE64


def test_create_document_rejects_files_larger_than_ten_mb(client):
    auth = register_user(client)
    too_large_size = 10 * 1024 * 1024 + 1
    too_large_payload = base64.b64encode(
        b"%PDF-" + (b"0" * (too_large_size - 5))
    ).decode("ascii")

    response = create_document(
        client,
        auth,
        size_in_bytes=too_large_size,
        file_data_base64=too_large_payload,
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Die Datei darf maximal 10 MB groß sein."


def test_create_document_rejects_invalid_file_data(client):
    auth = register_user(client)

    response = create_document(
        client,
        auth,
        size_in_bytes=4,
        file_data_base64="not valid base64",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Die Datei enthält keine gültigen Daten."


def test_create_document_rejects_file_data_that_does_not_match_mime_type(client):
    auth = register_user(client)

    response = create_document(
        client,
        auth,
        size_in_bytes=4,
        mime_type="application/pdf",
        file_data_base64="AQIDBA==",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Die Datei enthält keine gültigen Daten."


def test_create_document_rejects_mismatched_file_size(client):
    auth = register_user(client)

    response = create_document(
        client,
        auth,
        size_in_bytes=99,
        file_data_base64=VALID_PDF_BASE64,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Die angegebene Dateigröße stimmt nicht mit den Dateidaten überein."
    )


def test_patch_document_updates_editable_metadata(client):
    auth = register_user(client)
    create_response = create_document(client, auth)
    document_id = create_response.json()["id"]

    response = client.patch(
        f"/profiles/{auth['profile_id']}/documents/{document_id}",
        headers=auth["headers"],
        json={
            "name": "Laborwerte.pdf",
            "category": "laboratory",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Laborwerte.pdf"
    assert data["category"] == "laboratory"


def test_delete_document_soft_deletes_and_hides_entry(client, db_session):
    auth = register_user(client)
    create_response = create_document(client, auth)
    document_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/profiles/{auth['profile_id']}/documents/{document_id}",
        headers=auth["headers"],
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == (
        "Das Dokument wurde erfolgreich entfernt."
    )

    entry = db_session.get(DocumentEntry, document_id)
    assert entry is not None
    assert entry.deleted_at is not None

    list_response = client.get(
        f"/profiles/{auth['profile_id']}/documents",
        headers=auth["headers"],
    )
    get_response = client.get(
        f"/profiles/{auth['profile_id']}/documents/{document_id}",
        headers=auth["headers"],
    )

    assert list_response.status_code == 200
    assert list_response.json() == []
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Dieses Dokument wurde nicht gefunden."


def test_document_routes_require_profile_access(client):
    first_user = register_user(client, email="first-doc@example.com")
    second_user = register_user(client, email="second-doc@example.com")

    response = client.get(
        f"/profiles/{first_user['profile_id']}/documents",
        headers=second_user["headers"],
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this profile."


def test_deleted_documents_remain_in_database(client, db_session):
    auth = register_user(client)
    create_response = create_document(client, auth)
    document_id = create_response.json()["id"]

    client.delete(
        f"/profiles/{auth['profile_id']}/documents/{document_id}",
        headers=auth["headers"],
    )

    entries = db_session.exec(select(DocumentEntry)).all()
    assert len(entries) == 1
    assert entries[0].id == document_id
    assert entries[0].deleted_at is not None
