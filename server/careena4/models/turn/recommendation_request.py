from pydantic import Field

from careena4.models.common import PipelineModel
from careena4.models.domain import ConversationState, MedicalCase, RecommendationState
from careena4.models.input import SymptomInputDraft
from careena4.models.turn.input import DiaryEntry, MedicationEntry


class RecommendationRequestInput(PipelineModel):
    session_id: str | None = None
    turn_id: str | None = None
    response_history_messages: list[dict[str, str]] = Field(default_factory=list)
    diary_history: list[DiaryEntry] = Field(default_factory=list)
    medication_history: list[MedicationEntry] = Field(default_factory=list)
    persisted_medical_case: MedicalCase | None = None
    persisted_conversation_state: ConversationState | None = None
    persisted_recommendation_state: RecommendationState | None = None
    persisted_symptom_input_draft: SymptomInputDraft | None = None

    @classmethod
    def from_persisted_state(
        cls,
        *,
        session_id: str | None = None,
        turn_id: str | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
        diary_history: list[DiaryEntry] | None = None,
        medication_history: list[MedicationEntry] | None = None,
        persisted_medical_case: MedicalCase | None = None,
        persisted_conversation_state: ConversationState | None = None,
        persisted_recommendation_state: RecommendationState | None = None,
        persisted_symptom_input_draft: SymptomInputDraft | None = None,
    ) -> "RecommendationRequestInput":
        return cls(
            session_id=session_id,
            turn_id=turn_id,
            response_history_messages=list(conversation_messages or []),
            diary_history=diary_history or [],
            medication_history=medication_history or [],
            persisted_medical_case=persisted_medical_case,
            persisted_conversation_state=persisted_conversation_state,
            persisted_recommendation_state=persisted_recommendation_state,
            persisted_symptom_input_draft=persisted_symptom_input_draft,
        )
