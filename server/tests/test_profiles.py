# Created as part of the authentication and profile management test setup.
# Tests profile listing, creation, updating, access protection, and soft deletion.

from sqlmodel import select

from database.models import AccountProfileAccess, Profile


def register_user(client, email="profile@example.com"):
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


def test_get_profiles_returns_accessible_profiles(client):
    auth = register_user(client)

    response = client.get(
        "/profiles",
        headers=auth["headers"],
    )

    assert response.status_code == 200

    profiles = response.json()
    assert len(profiles) == 1
    assert profiles[0]["display_name"] == "Anna"
    assert profiles[0]["profile_type"] == "self"
    assert profiles[0]["role"] == "owner"


def test_create_child_profile_creates_guardian_access(client, db_session):
    auth = register_user(client)

    response = client.post(
        "/profiles",
        headers=auth["headers"],
        json={
            "display_name": "Ben",
            "date_of_birth": "2015-08-20",
            "biological_sex": "male",
            "height_cm": 140,
            "weight_kg": 35.5,
            "profile_type": "child",
            "relevant_preconditions_summary": "Asthma",
            "relevant_medications_summary": "Salbutamol bei Bedarf",
            "symptom_diary_summary": None,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["display_name"] == "Ben"
    assert data["profile_type"] == "child"
    assert data["height_cm"] == 140
    assert data["weight_kg"] == 35.5
    assert data["role"] == "guardian"

    profile = db_session.get(Profile, data["id"])
    access = db_session.exec(
        select(AccountProfileAccess).where(
            AccountProfileAccess.profile_id == data["id"]
        )
    ).first()

    assert profile is not None
    assert profile.display_name == "Ben"
    assert profile.height_cm == 140
    assert profile.weight_kg == 35.5
    assert profile.relevant_preconditions_summary == "Asthma"

    assert access is not None
    assert access.role == "guardian"


def test_get_profile_by_id_requires_access(client):
    first_user = register_user(client, email="first@example.com")
    second_user = register_user(client, email="second@example.com")

    response = client.get(
        f"/profiles/{first_user['profile_id']}",
        headers=second_user["headers"],
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this profile."


def test_patch_profile_updates_profile_for_allowed_role(client):
    auth = register_user(client)

    response = client.patch(
        f"/profiles/{auth['profile_id']}",
        headers=auth["headers"],
        json={
            "display_name": "Anna Updated",
            "height_cm": 171,
            "weight_kg": 70.5,
            "relevant_preconditions_summary": "Migräne",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["display_name"] == "Anna Updated"
    assert data["height_cm"] == 171
    assert data["weight_kg"] == 70.5
    assert data["relevant_preconditions_summary"] == "Migräne"
    assert data["role"] == "owner"


def test_delete_profile_soft_deletes_and_hides_profile(client, db_session):
    auth = register_user(client)

    create_response = client.post(
        "/profiles",
        headers=auth["headers"],
        json={
            "display_name": "Ben",
            "date_of_birth": "2015-08-20",
            "biological_sex": "male",
            "profile_type": "child",
            "relevant_preconditions_summary": "Asthma",
            "relevant_medications_summary": "Salbutamol bei Bedarf",
            "symptom_diary_summary": None,
        },
    )

    assert create_response.status_code == 200
    child_profile_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/profiles/{child_profile_id}",
        headers=auth["headers"],
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Profile deleted successfully."

    profile = db_session.get(Profile, child_profile_id)
    assert profile is not None
    assert profile.deleted_at is not None

    list_response = client.get(
        "/profiles",
        headers=auth["headers"],
    )

    assert list_response.status_code == 200

    profile_ids = [profile["id"] for profile in list_response.json()]
    assert child_profile_id not in profile_ids


def test_deleted_profile_returns_404(client):
    auth = register_user(client)

    create_response = client.post(
        "/profiles",
        headers=auth["headers"],
        json={
            "display_name": "Ben",
            "date_of_birth": "2015-08-20",
            "biological_sex": "male",
            "profile_type": "child",
        },
    )

    assert create_response.status_code == 200
    child_profile_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/profiles/{child_profile_id}",
        headers=auth["headers"],
    )

    assert delete_response.status_code == 200

    response = client.get(
        f"/profiles/{child_profile_id}",
        headers=auth["headers"],
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found."
