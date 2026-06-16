# Test case references: documents/Testfaelle_Backend.md#t04-symptome-und-input-drafts

from inputs.draft_service import (
    cancel_symptom_draft,
    get_symptom_draft,
    merge_extracted_symptoms,
    update_symptom_draft,
)


def test_input_draft_router_updates_and_clears_valid_session(client, session_manager):
    session_id = session_manager.create_session()

    initial_response = client.get(f"/input-drafts/{session_id}")
    assert initial_response.status_code == 200
    assert initial_response.json() == {
        "session_id": session_id,
        "symptoms": [],
    }

    update_response = client.patch(
        f"/input-drafts/{session_id}",
        json={"symptoms": [" Bauchschmerzen ", "", "Schmerzen"]},
    )
    assert update_response.status_code == 200
    assert update_response.json() == {
        "session_id": session_id,
        "symptoms": ["Bauchschmerzen"],
    }

    delete_response = client.delete(f"/input-drafts/{session_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": "Draft cancelled successfully.",
        "session_id": session_id,
    }
    assert get_symptom_draft(session_id) == []


def test_input_draft_router_rejects_unknown_session(client):
    response = client.get("/input-drafts/unknown-session")

    assert response.status_code == 404


def test_input_draft_router_requires_auth_for_profile_session(
    client,
    session_manager,
):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "draft-owner@example.com",
            "password": "secret123",
            "display_name": "Anna",
        },
    )
    data = register_response.json()
    session_id = session_manager.create_session(profile_id=data["profiles"][0]["id"])

    unauthenticated_response = client.get(f"/input-drafts/{session_id}")
    assert unauthenticated_response.status_code == 401

    authenticated_response = client.get(
        f"/input-drafts/{session_id}",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert authenticated_response.status_code == 200


def test_update_and_get_symptom_draft():
    session_id = "test-session-1"

    updated_symptoms = update_symptom_draft(
        session_id=session_id,
        symptoms=["Kopfschmerzen", "Uebelkeit"],
    )

    assert updated_symptoms == ["Kopfschmerzen", "Uebelkeit"]
    assert get_symptom_draft(session_id) == ["Kopfschmerzen", "Uebelkeit"]


def test_update_symptom_draft_removes_empty_values():
    session_id = "test-session-2"

    updated_symptoms = update_symptom_draft(
        session_id=session_id,
        symptoms=["Kopfschmerzen", "", "   ", "Uebelkeit"],
    )

    assert updated_symptoms == ["Kopfschmerzen", "Uebelkeit"]


def test_cancel_symptom_draft_removes_saved_data():
    session_id = "test-session-3"

    update_symptom_draft(
        session_id=session_id,
        symptoms=["Schwindel"],
    )

    cancel_symptom_draft(session_id)

    assert get_symptom_draft(session_id) == []


def test_get_symptom_draft_returns_empty_list_if_missing():
    assert get_symptom_draft("unknown-session") == []


def test_merge_extracted_symptoms_adds_only_new_labels():
    session_id = "test-session-4"

    update_symptom_draft(
        session_id=session_id,
        symptoms=["Kopfschmerzen"],
    )

    symptoms = merge_extracted_symptoms(
        session_id=session_id,
        symptoms=["Kopfschmerzen", "Schwindel"],
    )

    assert symptoms == ["Kopfschmerzen", "Schwindel"]


def test_merge_extracted_symptoms_cleans_and_deduplicates_labels():
    session_id = "test-session-multiple"

    symptoms = merge_extracted_symptoms(
        session_id=session_id,
        symptoms=[
            " Kopfschmerzen ",
            "kopfschmerzen",
            "",
            "   ",
            "Angst",
            "innere Unruhe",
        ],
    )

    assert symptoms == ["Kopfschmerzen", "Angst", "innere Unruhe"]


def test_merge_extracted_symptoms_keeps_psychological_complaints():
    session_id = "test-session-5"

    symptoms = merge_extracted_symptoms(
        session_id=session_id,
        symptoms=["Panik", "Schlaflosigkeit", "Ueberforderung"],
    )

    assert symptoms == ["Panik", "Schlaflosigkeit", "Ueberforderung"]


def test_merge_extracted_symptoms_deduplicates_generic_pain_variants():
    session_id = "test-session-pain-variants"

    symptoms = merge_extracted_symptoms(
        session_id=session_id,
        symptoms=["Schmerz", "Schmerzen", "Schmerze", "Shcmerzen"],
    )

    assert symptoms == ["Schmerz"]


def test_merge_extracted_symptoms_skips_generic_pain_after_specific_pain():
    session_id = "test-session-specific-before-generic-pain"

    update_symptom_draft(
        session_id=session_id,
        symptoms=["Ohrenschmerzen"],
    )

    symptoms = merge_extracted_symptoms(
        session_id=session_id,
        symptoms=["Schmerzen"],
    )

    assert symptoms == ["Ohrenschmerzen"]


def test_merge_extracted_symptoms_replaces_generic_pain_with_specific_pain():
    session_id = "test-session-generic-before-specific-pain"

    update_symptom_draft(
        session_id=session_id,
        symptoms=["Schmerzen"],
    )

    symptoms = merge_extracted_symptoms(
        session_id=session_id,
        symptoms=["Bauchschmerzen"],
    )

    assert symptoms == ["Bauchschmerzen"]


def test_merge_extracted_symptoms_deduplicates_location_pain_phrases():
    session_id = "test-session-location-pain-phrases"

    symptoms = merge_extracted_symptoms(
        session_id=session_id,
        symptoms=[
            "Bauchschmerzen",
            "Schmerzen im Bauch",
            "Schmerz am Bauch",
            "Bauch Schmerz",
        ],
    )

    assert symptoms == ["Bauchschmerzen"]


def test_merge_extracted_symptoms_deduplicates_linking_letter_pain_phrases():
    session_id = "test-session-linking-letter-pain-phrases"

    symptoms = merge_extracted_symptoms(
        session_id=session_id,
        symptoms=[
            "Ohrenschmerzen",
            "Schmerzen im Ohr",
        ],
    )

    assert symptoms == ["Ohrenschmerzen"]


def test_update_symptom_draft_prefers_specific_pain_labels():
    session_id = "test-session-update-pain-specificity"

    symptoms = update_symptom_draft(
        session_id=session_id,
        symptoms=["Schmerzen", "Ohrenschmerzen", "Bauch Schmerz"],
    )

    assert symptoms == ["Ohrenschmerzen", "Bauch Schmerz"]
