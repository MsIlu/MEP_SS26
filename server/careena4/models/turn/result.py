from pydantic import Field

from careena4.models.common import PipelineModel, ResponseMode
from careena4.models.domain import CaseTopic, ConversationState, MedicalCase, RecommendationState
from careena4.models.workflow import RecommendationResult


class TurnResult(PipelineModel):
    turn_id: str | None = None
    response_mode: ResponseMode
    response_text: str
    case_topic: CaseTopic | None = None
    medical_case: MedicalCase | None = None
    conversation_state: ConversationState
    recommendation_state: RecommendationState
    recommendation_result: RecommendationResult | None = None
    trace_notes: list[str] = Field(default_factory=list)
