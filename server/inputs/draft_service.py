# In-memory storage for temporary input drafts.
# This data is lost when the backend server restarts.
_draft_storage: dict[str, list[str]] = {}


def get_symptom_draft(session_id: str) -> list[str]:
    """
    Returns the current symptom draft for a session.
    If no draft exists, an empty list is returned.
    """

    return _draft_storage.get(session_id, [])


def update_symptom_draft(session_id: str, symptoms: list[str]) -> list[str]:
    """
    Updates the symptom draft for a session.
    Empty values are removed before saving.
    """

    cleaned_symptoms = [
        symptom.strip()
        for symptom in symptoms
        if symptom and symptom.strip()
    ]

    _draft_storage[session_id] = cleaned_symptoms

    return cleaned_symptoms


def cancel_symptom_draft(session_id: str) -> None:
    """
    Removes the symptom draft for a session.
    This is used when the user cancels the whole input process.
    """

    _draft_storage.pop(session_id, None)