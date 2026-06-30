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
            "temperatureC": 38.4,
            "note": "Seit dem Morgen",
            "source": "careena",
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
    assert data["temperatureC"] == 38.4
    assert data["note"] == "Seit dem Morgen"
    assert data["source"] == "careena"
    assert data["createdAt"] == "2026-06-12T09:30:00"
    assert data["updatedAt"] is not None

    entry = db_session.exec(select(SymptomDiaryEntry)).first()
    assert entry is not None
    assert entry.profile_id == auth["profile_id"]
    assert entry.body_area == "Kopf"
    assert entry.temperature_c == 38.4
    assert entry.source == "careena"


def test_update_symptom_changes_editable_fields(client, db_session):
    auth = register_user(client, email="symptom-update@example.com")
    create_response = client.post(
        f"/profiles/{auth['profile_id']}/symptoms",
        headers=auth["headers"],
        json={
            "date": "2026-06-12T00:00:00",
            "symptom": "Fieber",
            "intensity": 5,
            "temperatureC": 38.1,
            "note": "",
            "source": "careena",
        },
    )
    entry_id = create_response.json()["id"]

    response = client.patch(
        f"/profiles/{auth['profile_id']}/symptoms/{entry_id}",
        headers=auth["headers"],
        json={
            "intensity": 7,
            "temperatureC": 39.2,
            "note": "Am Abend gestiegen",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intensity"] == 7
    assert data["temperatureC"] == 39.2
    assert data["note"] == "Am Abend gestiegen"
    assert data["source"] == "careena"

    entry = db_session.get(SymptomDiaryEntry, entry_id)
    assert entry is not None
    assert entry.updated_at >= entry.created_at


def test_update_symptom_rejects_entry_from_another_profile(client):
    first_user = register_user(client, email="symptom-owner@example.com")
    second_user = register_user(client, email="symptom-attacker@example.com")
    created = client.post(
        f"/profiles/{first_user['profile_id']}/symptoms",
        headers=first_user["headers"],
        json={
            "date": "2026-06-12T00:00:00",
            "symptom": "Husten",
            "intensity": 3,
            "note": "",
        },
    )

    response = client.patch(
        f"/profiles/{first_user['profile_id']}/symptoms/{created.json()['id']}",
        headers=second_user["headers"],
        json={"intensity": 9},
    )

    assert response.status_code == 403


def test_update_symptom_validates_temperature(client):
    auth = register_user(client, email="symptom-temperature@example.com")
    created = client.post(
        f"/profiles/{auth['profile_id']}/symptoms",
        headers=auth["headers"],
        json={
            "date": "2026-06-12T00:00:00",
            "symptom": "Fieber",
            "intensity": 3,
            "note": "",
        },
    )

    response = client.patch(
        f"/profiles/{auth['profile_id']}/symptoms/{created.json()['id']}",
        headers=auth["headers"],
        json={"temperatureC": 48.0},
    )

    assert response.status_code == 422


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
