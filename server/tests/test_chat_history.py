# Test case references: documents/Testfaelle_Backend.md#t03-chat-history

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
            "status": "completed",
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
    assert entries[0]["created_at"].endswith(("Z", "+00:00"))
    assert entries[0]["messages"][0]["text"] == "Husten"
    assert entries[0]["status"] == "completed"
    assert entries[0]["updated_at"].endswith(("Z", "+00:00"))


def test_chat_history_can_update_active_entry(client):
    auth = register_user(client, email="active-history@example.com")

    create_response = client.post(
        "/chat-history",
        headers=auth["headers"],
        json={
            "profile_id": auth["profile_id"],
            "title": "Bauchschmerzen",
            "status": "active",
            "is_emergency": False,
            "recommendation": "",
            "messages": [
                {
                    "text": "Ich habe Bauchschmerzen",
                    "is_user": True,
                },
            ],
        },
    )

    assert create_response.status_code == 200

    history_id = create_response.json()["id"]

    update_response = client.patch(
        f"/chat-history/{history_id}",
        headers=auth["headers"],
        json={
            "title": "Bauchschmerzen",
            "status": "completed",
            "is_emergency": False,
            "recommendation": "Hausarztpraxis regulär",
            "next_steps": "Termin vereinbaren",
            "messages": [
                {
                    "text": "Ich habe Bauchschmerzen",
                    "is_user": True,
                },
                {
                    "text": "Bitte vereinbaren Sie einen Termin.",
                    "is_user": False,
                },
            ],
        },
    )

    assert update_response.status_code == 200

    body = update_response.json()
    assert body["id"] == history_id
    assert body["status"] == "completed"
    assert body["recommendation"] == "Hausarztpraxis regulär"
    assert body["next_steps"] == "Termin vereinbaren"
    assert len(body["messages"]) == 2


def test_chat_history_can_resume_active_entry(client):
    auth = register_user(client, email="resume-history@example.com")

    create_response = client.post(
        "/chat-history",
        headers=auth["headers"],
        json={
            "profile_id": auth["profile_id"],
            "title": "Durchfall",
            "status": "active",
            "session_id": "missing-session",
            "is_emergency": False,
            "recommendation": "",
            "messages": [
                {
                    "text": "Ich habe Durchfall",
                    "is_user": True,
                },
                {
                    "text": "Seit wann besteht der Durchfall?",
                    "is_user": False,
                },
            ],
        },
    )

    assert create_response.status_code == 200

    history_id = create_response.json()["id"]

    resume_response = client.post(
        f"/chat-history/{history_id}/resume",
        headers=auth["headers"],
    )

    assert resume_response.status_code == 200

    body = resume_response.json()
    assert body["session_id"] == "test-session-1"
    assert body["restored"] is True

    session_store = client.app.state.careena4_session_store
    restored_session = session_store.get("test-session-1")

    assert restored_session.messages == [
        {"role": "user", "content": "Ich habe Durchfall"},
        {"role": "assistant", "content": "Seit wann besteht der Durchfall?"},
    ]


def test_chat_history_can_continue_pending_assistant_response(client):
    auth = register_user(client, email="continue-history@example.com")

    create_response = client.post(
        "/chat-history",
        headers=auth["headers"],
        json={
            "profile_id": auth["profile_id"],
            "title": "Durchfall",
            "status": "waiting_for_assistant",
            "session_id": "missing-session",
            "is_emergency": False,
            "recommendation": "",
            "messages": [
                {
                    "text": "Ich habe Durchfall",
                    "is_user": True,
                },
            ],
        },
    )

    assert create_response.status_code == 200

    history_id = create_response.json()["id"]

    continue_response = client.post(
        f"/chat-history/{history_id}/continue",
        headers=auth["headers"],
    )

    assert continue_response.status_code == 200

    body = continue_response.json()
    assert body["session_id"] == "test-session-1"
    assert body["response"] == (
        "Bitte trinken Sie ausreichend und beobachten Sie den Verlauf."
    )
    assert body["red_flag"] is False

    history_response = client.get(
        f"/chat-history/{auth['profile_id']}",
        headers=auth["headers"],
    )

    assert history_response.status_code == 200

    entries = history_response.json()
    assert entries[0]["status"] == "active"
    assert entries[0]["messages"][-1]["is_user"] is False
    assert entries[0]["messages"][-1]["text"] == (
        "Bitte trinken Sie ausreichend und beobachten Sie den Verlauf."
    )


def test_chat_history_requires_profile_access(client):
    first_user = register_user(client, email="first-history@example.com")
    second_user = register_user(client, email="second-history@example.com")

    response = client.get(
        f"/chat-history/{first_user['profile_id']}",
        headers=second_user["headers"],
    )

    assert response.status_code == 403
