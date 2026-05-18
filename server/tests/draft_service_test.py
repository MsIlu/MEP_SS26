from inputs.draft_service import (
    get_symptom_draft,
    update_symptom_draft,
    cancel_symptom_draft,
)

# Tests saving and loading a symptom draft.
def test_update_and_get_symptom_draft():
    session_id = "test-session-1"

    updated_symptoms = update_symptom_draft(
        session_id=session_id,
        symptoms=["Kopfschmerzen", "Übelkeit"],
    )

    assert updated_symptoms == ["Kopfschmerzen", "Übelkeit"]
    assert get_symptom_draft(session_id) == ["Kopfschmerzen", "Übelkeit"]

# Tests that empty symptom values are removed before saving.
def test_update_symptom_draft_removes_empty_values():
    session_id = "test-session-2"

    updated_symptoms = update_symptom_draft(
        session_id=session_id,
        symptoms=["Kopfschmerzen", "", "   ", "Übelkeit"],
    )

    assert updated_symptoms == ["Kopfschmerzen", "Übelkeit"]

# Tests that cancelling removes the stored symptom draft.
def test_cancel_symptom_draft_removes_saved_data():
    session_id = "test-session-3"

    update_symptom_draft(
        session_id=session_id,
        symptoms=["Schwindel"],
    )

    cancel_symptom_draft(session_id)

    assert get_symptom_draft(session_id) == []

# Tests that unknown sessions return an empty symptom list.
def test_get_symptom_draft_returns_empty_list_if_missing():
    session_id = "unknown-session"

    assert get_symptom_draft(session_id) == []