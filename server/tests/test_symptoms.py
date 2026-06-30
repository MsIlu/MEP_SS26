# Test case references: documents/Testfaelle_Backend.md#t04-symptome-und-input-drafts

from sqlmodel import select

from database.models import SymptomDiaryEntry
from tests.test_profiles import register_user


def test_create_symptom_stores_entry(client, db_session):
    auth = register_user(client)

    response = client.post(
        f"/profiles/{auth['profile_id']}/symptoms",
        headers=auth["headers"],
        json={
            "date": "2026-06-12T00:00:00",
            "symptom": "Kopfschmerzen",
            "bodyArea": "Kopf",
            "intensity": 7,
            "note": "Seit dem Morgen",
            "createdAt": "2026-06-12T09:30:00",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] is not None
    assert data["profile_id"] == auth["profile_id"]
    assert data["symptom"] == "Kopfschmerzen"
    assert data["bodyArea"] == "Kopf"
    assert data["intensity"] == 7
    assert data["note"] == "Seit dem Morgen"
    assert data["createdAt"] == "2026-06-12T09:30:00"

    entry = db_session.exec(select(SymptomDiaryEntry)).first()
    assert entry is not None
    assert entry.profile_id == auth["profile_id"]
    assert entry.body_area == "Kopf"


def test_get_symptoms_returns_profile_entries(client):
    auth = register_user(client)

    client.post(
        f"/profiles/{auth['profile_id']}/symptoms",
        headers=auth["headers"],
        json={
            "date": "2026-06-12T00:00:00",
            "symptom": "Übelkeit",
            "intensity": 4,
            "note": "",
        },
    )

    response = client.get(
        f"/profiles/{auth['profile_id']}/symptoms",
        headers=auth["headers"],
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["symptom"] == "Übelkeit"
    assert data[0]["bodyArea"] == ""


def test_delete_symptom_removes_entry_from_database(client, db_session):
    auth = register_user(client)

    create_response = client.post(
        f"/profiles/{auth['profile_id']}/symptoms",
        headers=auth["headers"],
        json={
            "date": "2026-06-12T00:00:00",
            "symptom": "Kopfschmerzen",
            "intensity": 4,
            "note": "",
        },
    )

    response = client.delete(
        f"/profiles/{auth['profile_id']}/symptoms/{create_response.json()['id']}",
        headers=auth["headers"],
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Symptom entry deleted successfully."

    remaining_entries = db_session.exec(select(SymptomDiaryEntry)).all()
    assert remaining_entries == []


def test_update_symptom_changes_entry_in_database(client, db_session):
    auth = register_user(client)

    create_response = client.post(
        f"/profiles/{auth['profile_id']}/symptoms",
        headers=auth["headers"],
        json={
            "date": "2026-06-12T00:00:00",
            "symptom": "Kopfschmerzen",
            "bodyArea": "Kopf",
            "intensity": 4,
            "note": "Morgens",
        },
    )

    entry_id = create_response.json()["id"]
    response = client.patch(
        f"/profiles/{auth['profile_id']}/symptoms/{entry_id}",
        headers=auth["headers"],
        json={
            "date": "2026-06-13T00:00:00",
            "symptom": "Bauchschmerzen",
            "bodyArea": "Bauch",
            "intensity": 7,
            "note": "Nach dem Essen",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == entry_id
    assert data["symptom"] == "Bauchschmerzen"
    assert data["bodyArea"] == "Bauch"
    assert data["intensity"] == 7
    assert data["note"] == "Nach dem Essen"

    entry = db_session.get(SymptomDiaryEntry, entry_id)
    assert entry is not None
    assert entry.symptom == "Bauchschmerzen"
    assert entry.body_area == "Bauch"
    assert entry.intensity == 7


def test_create_symptom_requires_profile_access(client):
    first_user = register_user(client, email="symptom-first@example.com")
    second_user = register_user(client, email="symptom-second@example.com")

    response = client.post(
        f"/profiles/{first_user['profile_id']}/symptoms",
        headers=second_user["headers"],
        json={
            "date": "2026-06-12T00:00:00",
            "symptom": "Husten",
            "intensity": 3,
            "note": "",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this profile."


def test_create_symptom_validates_intensity(client):
    auth = register_user(client)

    response = client.post(
        f"/profiles/{auth['profile_id']}/symptoms",
        headers=auth["headers"],
        json={
            "date": "2026-06-12T00:00:00",
            "symptom": "Schwindel",
            "intensity": 11,
            "note": "",
        },
    )

    assert response.status_code == 422
