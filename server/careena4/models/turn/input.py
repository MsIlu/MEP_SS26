from pydantic import Field

from careena4.models.common import PipelineModel
from careena4.models.domain import ConversationState, MedicalCase, RecommendationState
from careena4.models.input import SymptomInputDraft


ENTRY_HISTORY_LIMIT = 4
EXTRACTION_HISTORY_LIMIT = 4
RESPONSE_HISTORY_LIMIT = 6


class DiaryEntry(PipelineModel):
    """One symptom diary entry from the user's persistent health diary."""
    date: str
    symptom: str
    body_area: str = ""
    intensity: int
    note: str = ""


class ProfileSnapshot(PipelineModel):
    """Minimal profile data passed from the server layer into the chat pipeline.

    Intentionally contains no database types — only plain values so the
    careena4 application layer stays independent of the profiles service.
    """
    display_name: str
    profile_type: str  # "self" | "child" | "other"
    age: int | None = None
    sex: str | None = None  # "female" | "male" | "diverse" | None


class TurnInput(PipelineModel):
    message: str
    session_id: str | None = None
    turn_id: str | None = None
    profile_id: int | None = None
    diary_history: list[DiaryEntry] = Field(default_factory=list)
    entry_history_messages: list[dict[str, str]] = Field(default_factory=list)
    extraction_history_messages: list[dict[str, str]] = Field(default_factory=list)
    response_history_messages: list[dict[str, str]] = Field(default_factory=list)
    persisted_medical_case: MedicalCase | None = None
    persisted_conversation_state: ConversationState | None = None
    persisted_recommendation_state: RecommendationState | None = None
    persisted_symptom_input_draft: SymptomInputDraft | None = None

    @classmethod
    def from_persisted_state(
        cls,
        *,
        message: str,
        session_id: str | None = None,
        turn_id: str | None = None,
        profile_id: int | None = None,
        diary_history: list[DiaryEntry] | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
        persisted_medical_case: MedicalCase | None = None,
        persisted_conversation_state: ConversationState | None = None,
        persisted_recommendation_state: RecommendationState | None = None,
        persisted_symptom_input_draft: SymptomInputDraft | None = None,
    ) -> "TurnInput":
        history = list(conversation_messages or [])
        return cls(
            message=message,
            session_id=session_id,
            turn_id=turn_id,
            profile_id=profile_id,
            diary_history=diary_history or [],
            entry_history_messages=_recent_history(history, ENTRY_HISTORY_LIMIT),
            extraction_history_messages=_recent_history(history, EXTRACTION_HISTORY_LIMIT),
            response_history_messages=_recent_history(history, RESPONSE_HISTORY_LIMIT),
            persisted_medical_case=persisted_medical_case,
            persisted_conversation_state=persisted_conversation_state,
            persisted_recommendation_state=persisted_recommendation_state,
            persisted_symptom_input_draft=persisted_symptom_input_draft,
        )


def _recent_history(messages: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    if limit <= 0:
        return []
    return list(messages[-limit:])
