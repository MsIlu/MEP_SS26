from careena4.models.interpretation import TurnInterpretation
from careena4.models.understanding import CurrentTurnUnderstanding
from pydantic import Field

from careena4.models.common import PipelineModel, ResponseMode
from careena4.models.domain import ConversationState, MedicalCase, RecommendationState
from careena4.models.input import SymptomInputDraft
from careena4.models.workflow import RecommendationResult


class TurnResult(PipelineModel):
    turn_id: str | None = None
    response_mode: ResponseMode
    response_text: str
    medical_case: MedicalCase | None = None
    conversation_state: ConversationState
    recommendation_state: RecommendationState
    recommendation_result: RecommendationResult | None = None
    symptom_input_draft: SymptomInputDraft | None = None
    turn_interpretation: TurnInterpretation | None = None
    current_turn_understanding: CurrentTurnUnderstanding | None = None
    trace_notes: list[str] = Field(default_factory=list)
