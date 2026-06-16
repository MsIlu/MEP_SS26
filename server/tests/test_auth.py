# Test case references: documents/Testfaelle_Backend.md#t01-auth-und-account-management
# Created as part of the authentication and profile management test setup.
# Tests registration and duplicate email handling.

from sqlmodel import select

from database.models import AccountProfileAccess, Profile, User


def test_register_creates_user_profile_and_access_entry(client, db_session):
    response = client.post(
        "/auth/register",
        json={
            "email": "anna@example.com",
            "password": "12345678",
            "display_name": "Anna",
            "date_of_birth": "2000-04-12",
            "biological_sex": "female",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["account"]["email"] == "anna@example.com"
    assert len(data["profiles"]) == 1
    assert data["profiles"][0]["display_name"] == "Anna"
    assert data["profiles"][0]["profile_type"] == "self"
    assert data["profiles"][0]["role"] == "owner"

    user = db_session.exec(select(User)).first()
    profile = db_session.exec(select(Profile)).first()
    access = db_session.exec(select(AccountProfileAccess)).first()

    assert user is not None
    assert profile is not None
    assert access is not None

    assert user.email == "anna@example.com"
    assert user.password_hash != "12345678"
    assert user.is_active is True
    assert user.active_profile_id == profile.id

    assert profile.display_name == "Anna"
    assert profile.profile_type == "self"

    assert access.account_id == user.id
    assert access.profile_id == profile.id
    assert access.role == "owner"


def test_register_rejects_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "12345678",
        "display_name": "Anna",
        "date_of_birth": "2000-04-12",
        "biological_sex": "female",
    }

    first_response = client.post("/auth/register", json=payload)
    #print(first_response.status_code, first_response.json())

    second_response = client.post("/auth/register", json=payload)
    #print(second_response.status_code, second_response.json())

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email is already registered."

def test_login_succeeds_with_valid_credentials(client):
    client.post(
        "/auth/register",
            json={
                "email": "login@example.com",
                "password": "12345678",
                "display_name": "Anna",
                "date_of_birth": "2000-04-12",
                "biological_sex": "female",
            },
        )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["access_token"]
    assert data["account"]["email"] == "login@example.com"
    assert len(data["profiles"]) == 1
    assert data["profiles"][0]["role"] == "owner"


def test_login_fails_with_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "email": "wrong-password@example.com",
            "password": "12345678",
            "display_name": "Anna",
            "date_of_birth": "2000-04-12",
            "biological_sex": "female",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrong-password@example.com",
            "password": "wrong",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_me_requires_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_returns_current_account_with_token(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "me@example.com",
            "password": "12345678",
            "display_name": "Anna",
            "date_of_birth": "2000-04-12",
            "biological_sex": "female",
        },
    )

    token = register_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_delete_account_soft_deletes_user_and_blocks_login(client, db_session):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "delete@example.com",
            "password": "12345678",
            "display_name": "Anna",
            "date_of_birth": "2000-04-12",
            "biological_sex": "female",
        },
    )

    token = register_response.json()["access_token"]

    delete_response = client.delete(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Account deleted successfully."

    user = db_session.exec(
        select(User).where(User.email == "delete@example.com")
    ).first()

    assert user is not None
    assert user.is_active is False
    assert user.deleted_at is not None

    login_response = client.post(
        "/auth/login",
        json={
            "email": "delete@example.com",
            "password": "12345678",
        },
    )

    assert login_response.status_code == 403
    assert login_response.json()["detail"] == "Account is inactive."
