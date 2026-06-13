# Tests medication creation, listing, updates, access protection, and deletion.

from sqlmodel import select

from database.models import MedicationEntry


def register_user(client, email="medication@example.com"):
    """
    Register a user and return token, headers and initial profile id.
    """
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


def create_medication(client, auth, **overrides):
    """
    Create a medication entry for the registered user's initial profile.
    """
    payload = {
        "name": "Aspirin",
        "dose": "500 mg",
        "intake_hour": 8,
        "intake_minute": 30,
        "frequency": "daily",
        "reminders_enabled": True,
    }
    payload.update(overrides)

    return client.post(
        f"/profiles/{auth['profile_id']}/medications",
        headers=auth["headers"],
        json=payload,
    )


def test_create_medication_persists_profile_scoped_entry(client, db_session):
    auth = register_user(client)

    response = create_medication(
        client,
        auth,
        catalog_item={
            "id": "aspirin-500",
            "name": "Aspirin",
            "active_substance": "Acetylsalicylic acid",
            "strength": "500 mg",
            "dosage_form": "Tablet",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["profile_id"] == auth["profile_id"]
    assert data["name"] == "Aspirin"
    assert data["dose"] == "500 mg"
    assert data["intake_hour"] == 8
    assert data["intake_minute"] == 30
    assert data["frequency"] == "daily"
    assert data["reminders_enabled"] is True
    assert data["taken_date_keys"] == []
    assert data["catalog_item"]["id"] == "aspirin-500"

    entry = db_session.get(MedicationEntry, data["id"])
    assert entry is not None
    assert entry.profile_id == auth["profile_id"]
    assert entry.catalog_item_id == "aspirin-500"


def test_create_medication_rejects_duplicate_active_schedule(client):
    auth = register_user(client)
    first_response = create_medication(client, auth)

    duplicate_response = create_medication(
        client,
        auth,
        name=" aspirin ",
        dose="500 MG",
    )

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == (
        "Medication already exists for this profile."
    )


def test_create_medication_allows_duplicate_after_soft_delete(client):
    auth = register_user(client)
    create_response = create_medication(client, auth)
    medication_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/profiles/{auth['profile_id']}/medications/{medication_id}",
        headers=auth["headers"],
    )
    recreate_response = create_medication(client, auth)

    assert delete_response.status_code == 200
    assert recreate_response.status_code == 200


def test_list_medications_returns_entries_in_intake_order(client):
    auth = register_user(client)

    late_response = create_medication(
        client,
        auth,
        name="Late",
        intake_hour=20,
        intake_minute=0,
    )
    early_response = create_medication(
        client,
        auth,
        name="Early",
        intake_hour=7,
        intake_minute=15,
    )

    assert late_response.status_code == 200
    assert early_response.status_code == 200

    response = client.get(
        f"/profiles/{auth['profile_id']}/medications",
        headers=auth["headers"],
    )

    assert response.status_code == 200
    assert [entry["name"] for entry in response.json()] == ["Early", "Late"]


def test_patch_medication_updates_editable_fields(client):
    auth = register_user(client)
    create_response = create_medication(client, auth)
    medication_id = create_response.json()["id"]

    response = client.patch(
        f"/profiles/{auth['profile_id']}/medications/{medication_id}",
        headers=auth["headers"],
        json={
            "dose": "250 mg",
            "frequency": "twice_daily",
            "second_intake_hour": 20,
            "second_intake_minute": 0,
            "reminders_enabled": False,
            "taken_date_keys": ["2026-06-11:0"],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["dose"] == "250 mg"
    assert data["frequency"] == "twice_daily"
    assert data["second_intake_hour"] == 20
    assert data["second_intake_minute"] == 0
    assert data["reminders_enabled"] is False
    assert data["taken_date_keys"] == ["2026-06-11:0"]


def test_patch_medication_rejects_duplicate_active_schedule(client):
    auth = register_user(client)
    existing_response = create_medication(client, auth)
    other_response = create_medication(
        client,
        auth,
        name="Ibuprofen",
        dose="400 mg",
        intake_hour=10,
        intake_minute=0,
    )

    response = client.patch(
        f"/profiles/{auth['profile_id']}/medications/{other_response.json()['id']}",
        headers=auth["headers"],
        json={
            "name": existing_response.json()["name"],
            "dose": existing_response.json()["dose"],
            "intake_hour": existing_response.json()["intake_hour"],
            "intake_minute": existing_response.json()["intake_minute"],
            "frequency": existing_response.json()["frequency"],
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Medication already exists for this profile."


def test_delete_medication_soft_deletes_and_hides_entry(client, db_session):
    auth = register_user(client)
    create_response = create_medication(client, auth)
    medication_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/profiles/{auth['profile_id']}/medications/{medication_id}",
        headers=auth["headers"],
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Medication deleted successfully."

    entry = db_session.get(MedicationEntry, medication_id)
    assert entry is not None
    assert entry.deleted_at is not None

    list_response = client.get(
        f"/profiles/{auth['profile_id']}/medications",
        headers=auth["headers"],
    )
    get_response = client.get(
        f"/profiles/{auth['profile_id']}/medications/{medication_id}",
        headers=auth["headers"],
    )

    assert list_response.status_code == 200
    assert list_response.json() == []
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Medication not found."


def test_medication_routes_require_profile_access(client):
    first_user = register_user(client, email="first-med@example.com")
    second_user = register_user(client, email="second-med@example.com")

    response = client.get(
        f"/profiles/{first_user['profile_id']}/medications",
        headers=second_user["headers"],
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this profile."


def test_create_medication_requires_complete_second_intake_time(client):
    auth = register_user(client)

    response = create_medication(
        client,
        auth,
        second_intake_hour=20,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Second intake time must include both hour and minute."
    )


def test_deleted_medications_remain_in_database(client, db_session):
    auth = register_user(client)
    create_response = create_medication(client, auth)
    medication_id = create_response.json()["id"]

    client.delete(
        f"/profiles/{auth['profile_id']}/medications/{medication_id}",
        headers=auth["headers"],
    )

    entries = db_session.exec(select(MedicationEntry)).all()
    assert len(entries) == 1
    assert entries[0].id == medication_id
    assert entries[0].deleted_at is not None
