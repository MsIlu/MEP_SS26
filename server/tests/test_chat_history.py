def register_user(client, email="history@example.com"):
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
        "profile_id": data["profiles"][0]["id"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
    }


def test_chat_history_is_profile_bound_and_sorted(client):
    auth = register_user(client)

    first_response = client.post(
        "/chat-history",
        headers=auth["headers"],
        json={
            "profile_id": auth["profile_id"],
            "title": "Kopfschmerzen",
            "is_emergency": False,
            "recommendation": "Erste Empfehlung",
            "next_steps": "Abwarten",
            "messages": [
                {
                    "text": "Kopfschmerzen",
                    "is_user": True,
                },
                {
                    "text": "Erste Empfehlung",
                    "is_user": False,
                    "can_export_pdf": True,
                },
            ],
        },
    )
    second_response = client.post(
        "/chat-history",
        headers=auth["headers"],
        json={
            "profile_id": auth["profile_id"],
            "title": "Husten",
            "is_emergency": True,
            "recommendation": "Zweite Empfehlung",
            "messages": [
                {
                    "text": "Husten",
                    "is_user": True,
                },
            ],
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    response = client.get(
        f"/chat-history/{auth['profile_id']}",
        headers=auth["headers"],
    )

    assert response.status_code == 200

    entries = response.json()
    assert [entry["recommendation"] for entry in entries] == [
        "Zweite Empfehlung",
        "Erste Empfehlung",
    ]
    assert entries[0]["profile_id"] == auth["profile_id"]
    assert entries[0]["title"] == "Husten"
    assert entries[0]["is_emergency"] is True
    assert entries[0]["messages"][0]["text"] == "Husten"


def test_chat_history_requires_profile_access(client):
    first_user = register_user(client, email="first-history@example.com")
    second_user = register_user(client, email="second-history@example.com")

    response = client.get(
        f"/chat-history/{first_user['profile_id']}",
        headers=second_user["headers"],
    )

    assert response.status_code == 403
