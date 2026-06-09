from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.domain import DialogueState, MedicalCase, PendingFollowup
from careena_pipeline3.models.workflow import AssessmentReadiness
from careena_pipeline3.models.workflow import RecommendationResult
from careena_pipeline3.models.turn.safety_state import SafetyState


class TurnContext(PipelineModel):
    active_modules: list[str] = Field(default_factory=list)
    pending_followup: PendingFollowup | None = None
    case_update_dialogue_consequences: list[str] = Field(default_factory=list)
    response_mode: str | None = None
    response_text: str | None = None
    recommendation_result: RecommendationResult | None = None
    person_reference_present: bool = False
    multi_person_context: bool = False
    subject_relation_unclear: bool = False
    trace_notes: list[str] = Field(default_factory=list)
    raw_safety: SafetyState = Field(default_factory=SafetyState)
    extraction_safety: SafetyState = Field(default_factory=SafetyState)
    case_safety: SafetyState = Field(default_factory=SafetyState)
    medical_case: MedicalCase | None = None
    dialogue_state: DialogueState = Field(default_factory=DialogueState)
    assessment_readiness: AssessmentReadiness = Field(default_factory=AssessmentReadiness)
