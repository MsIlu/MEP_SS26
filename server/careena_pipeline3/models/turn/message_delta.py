from pydantic import Field

from careena_pipeline3.models.common import MessageRole, PipelineModel, PlannerModule
from careena_pipeline3.models.domain import CaseObservation, StagedFollowupAnswer, Subject


class MessageCaseDelta(PipelineModel):
    subject: Subject | None = None
    observations_added: list[CaseObservation] = Field(default_factory=list)
    negated_observations_added: list[CaseObservation] = Field(default_factory=list)

    @property
    def all_observations(self) -> list[CaseObservation]:
        return self.observations_added + self.negated_observations_added

    @property
    def has_updates(self) -> bool:
        return self.subject is not None or bool(self.all_observations)


class MessageIntentSignals(PipelineModel):
    intent_category: str | None = None
    is_medical: bool = False
    extraction_required: bool = False
    intent_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    message_role: MessageRole = "new_information"
    possible_new_topic: bool = False


class MessageRequirementSignals(PipelineModel):
    active_modules: list[str] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    resolved_fields: list[str] = Field(default_factory=list)


class MessagePlannerSignals(PipelineModel):
    recommended_modules: list[PlannerModule] = Field(default_factory=list)
    recommendation_requested: bool = False


class MessageTraceSignals(PipelineModel):
    notes: list[str] = Field(default_factory=list)
    gateway_category: str | None = None
    gateway_message_role: MessageRole | None = None
    gateway_extraction_required: bool | None = None
    llm_intent_category: str | None = None
    llm_is_medical: bool | None = None
    llm_extraction_required: bool | None = None
    llm_message_role: MessageRole | None = None


class MessageStagingSignals(PipelineModel):
    staged_followup_answers: list[StagedFollowupAnswer] = Field(default_factory=list)
    clear_staged_followup_answers: bool = False


class MessageDelta(PipelineModel):
    """
    Transitional bridge from extraction output to canonical state mutation.

    This is intentionally not treated as the long-term Call-2 target contract.
    It currently exists so state progression can move forward while the cleaner
    extraction contract is designed separately.
    """

    raw_text: str
    case_delta: MessageCaseDelta = Field(default_factory=MessageCaseDelta)
    intent_signals: MessageIntentSignals = Field(default_factory=MessageIntentSignals)
    requirement_signals: MessageRequirementSignals = Field(default_factory=MessageRequirementSignals)
    planner_signals: MessagePlannerSignals = Field(default_factory=MessagePlannerSignals)
    trace_signals: MessageTraceSignals = Field(default_factory=MessageTraceSignals)
    staging_signals: MessageStagingSignals = Field(default_factory=MessageStagingSignals)

    @property
    def case_payload(self) -> MessageCaseDelta:
        return self.case_delta

    @property
    def subject_update(self) -> Subject | None:
        return self.case_delta.subject
