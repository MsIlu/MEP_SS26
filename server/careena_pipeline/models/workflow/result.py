from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import ResponseMode
from careena_pipeline.models.domain.case import MedicalCase
from careena_pipeline.models.domain.dialogue import DialogueState
from careena_pipeline.models.workflow.message_update import MessageUpdate
from careena_pipeline.models.workflow.readiness import AssessmentReadiness
from careena_pipeline.models.workflow.recommendation import Recommendation
from careena_pipeline.models.workflow.recommendation_gate import RecommendationGateDecision
from careena_pipeline.models.workflow.safety import SafetyResult


class CareenaPipelineResult(PipelineModel):
    raw_text: str
    safety: SafetyResult
    case: MedicalCase | None = None
    dialogue_state: DialogueState | None = None
    message_update: MessageUpdate | None = None
    readiness: AssessmentReadiness | None = None
    recommendation_gate: RecommendationGateDecision | None = None
    recommendation: Recommendation | None = None
    response_mode: ResponseMode
