import re
from collections.abc import Iterable

# In-memory storage for temporary input drafts.
# This data is lost when the backend server restarts.
_draft_storage: dict[str, list[str]] = {}

_GERMAN_CHAR_REPLACEMENTS = str.maketrans(
    {
        "\u00e4": "ae",
        "\u00f6": "oe",
        "\u00fc": "ue",
        "\u00df": "ss",
    }
)


def get_symptom_draft(session_id: str) -> list[str]:
    """
    Return the current symptom draft for a session.
    """

    return _draft_storage.get(session_id, [])


def update_symptom_draft(session_id: str, symptoms: list[str]) -> list[str]:
    """
    Update the symptom draft for a session.

    Empty values are removed before saving.
    """

    cleaned_symptoms = _merge_symptom_labels([], symptoms)

    _draft_storage[session_id] = cleaned_symptoms

    return cleaned_symptoms


def merge_extracted_symptoms(
    session_id: str,
    symptoms: Iterable[str],
) -> list[str]:
    """
    Add extracted symptom labels to the current draft.

    Symptom recognition is handled by the structured extraction layer. This
    function only owns draft storage, cleanup and stable de-duplication.
    """

    current_symptoms = get_symptom_draft(session_id)
    merged_symptoms = _merge_symptom_labels(current_symptoms, symptoms)

    if merged_symptoms != current_symptoms:
        _draft_storage[session_id] = merged_symptoms

    return merged_symptoms


def cancel_symptom_draft(session_id: str) -> None:
    """
    Remove the symptom draft for a session.
    """

    _draft_storage.pop(session_id, None)


def _merge_symptom_labels(
    existing_symptoms: Iterable[str],
    new_symptoms: Iterable[str],
) -> list[str]:
    """
    Merge symptom labels with stable ordering and conservative normalization.

    Pain terms are normalized just enough to avoid common duplicates:
    "Schmerz", "Schmerzen", "Schmerze" and the typo "Shcmerzen" share a key.
    Specific pain labels such as "Ohrenschmerzen" stay separate, but make a
    later generic pain label unnecessary.
    """

    merged_symptoms: list[str] = []
    existing_keys: set[str] = set()

    for symptom in [*existing_symptoms, *new_symptoms]:
        label = symptom.strip()

        if not label:
            continue

        key = _symptom_key(label)

        if key in existing_keys:
            continue

        if _is_generic_pain_key(key) and _contains_specific_pain(existing_keys):
            continue

        if _is_specific_pain_key(key):
            merged_symptoms = [
                existing_label
                for existing_label in merged_symptoms
                if not _is_generic_pain_key(_symptom_key(existing_label))
            ]
            existing_keys = {
                existing_key
                for existing_key in existing_keys
                if not _is_generic_pain_key(existing_key)
            }

        merged_symptoms.append(label)
        existing_keys.add(key)

    return merged_symptoms


def _symptom_key(label: str) -> str:
    """
    Build a de-duplication key without changing the displayed symptom label.
    """

    normalized = label.casefold().translate(_GERMAN_CHAR_REPLACEMENTS)
    normalized = normalized.replace("shc", "sch")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    if normalized.endswith("schmerzen"):
        normalized = normalized[:-2]
    elif normalized.endswith("schmerze"):
        normalized = normalized[:-1]

    if normalized.endswith(" schmerz"):
        normalized = normalized.removesuffix(" schmerz") + "schmerz"

    return normalized


def _is_generic_pain_key(key: str) -> bool:
    return key == "schmerz"


def _is_specific_pain_key(key: str) -> bool:
    return key.endswith("schmerz") and not _is_generic_pain_key(key)


def _contains_specific_pain(keys: Iterable[str]) -> bool:
    return any(_is_specific_pain_key(key) for key in keys)
