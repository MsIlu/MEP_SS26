from dataclasses import dataclass

from pydantic import Field

from careena_pipeline.state.module_registry import ModuleName, RequirementRef
from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import (
    MessageRole,
    PlannerModule,
)
from careena_pipeline.models.domain.observation import CaseObservation
from careena_pipeline.models.domain.subject import Subject
from careena_pipeline.models.workflow.intent_gateway import IntentGateway


@dataclass(frozen=True)
class MessageCasePayload:
    subject: Subject | None
    observations_added: list[CaseObservation]
    negated_observations_added: list[CaseObservation]

    @property
    def all_observations(self) -> list[CaseObservation]:
        return self.observations_added + self.negated_observations_added

    @property
    def has_updates(self) -> bool:
        return self.subject is not None or bool(self.all_observations)


@dataclass(frozen=True)
class MessageRequirementHints:
    active_modules: list[ModuleName]
    required_fields: list[RequirementRef]
    resolved_fields: list[RequirementRef]

    @property
    def has_signals(self) -> bool:
        return bool(
            self.active_modules
            or self.required_fields
            or self.resolved_fields
        )


@dataclass(frozen=True)
class MessagePlannerHints:
    recommended_modules: list[PlannerModule]
    recommendation_requested: bool

    @property
    def has_signals(self) -> bool:
        return self.recommendation_requested or bool(self.recommended_modules)


class MessageUpdate(PipelineModel):
    """
    Bridging result of the message-processing path.

    This object intentionally mixes several signal families for the current
    architecture:
    - final message-level result used by merge/state
    - gateway guidance traces from Call 1
    - direct LLM traces from Call 2
    - requirement/module hints for later decision layers

    The fields therefore do not all carry the same truth weight. Phase 2
    documentation treats this object as an explicit signal bundle, not as a
    pure extraction model.
    """

    raw_text: str
    intent_category: str | None = None
    is_medical: bool = False
    extraction_required: bool = False
    intent_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    subject: Subject | None = None
    observations_added: list[CaseObservation] = Field(default_factory=list)
    negated_observations_added: list[CaseObservation] = Field(default_factory=list)
    user_requests_recommendation: bool = False
    possible_new_topic: bool = False
    notes: list[str] = Field(default_factory=list)
    message_role: MessageRole = "new_information"
    intent_gateway: IntentGateway | None = None
    llm_intent_category: str | None = None
    llm_is_medical: bool | None = None
    llm_extraction_required: bool | None = None
    llm_message_role: MessageRole | None = None
    active_modules: list[ModuleName] = Field(default_factory=list)
    required_fields: list[RequirementRef] = Field(default_factory=list)
    resolved_fields: list[RequirementRef] = Field(default_factory=list)
    recommended_modules: list[PlannerModule] = Field(default_factory=list)

    @property
    def subject_update(self) -> Subject | None:
        return self.subject

    @property
    def case_payload(self) -> MessageCasePayload:
        return MessageCasePayload(
            subject=self.subject,
            observations_added=list(self.observations_added),
            negated_observations_added=list(self.negated_observations_added),
        )

    @property
    def requirement_hints(self) -> MessageRequirementHints:
        return MessageRequirementHints(
            active_modules=list(self.active_modules),
            required_fields=list(self.required_fields),
            resolved_fields=list(self.resolved_fields),
        )

    @property
    def planner_hints(self) -> MessagePlannerHints:
        return MessagePlannerHints(
            recommended_modules=list(self.recommended_modules),
            recommendation_requested=self.user_requests_recommendation,
        )

    @property
    def extracted_requirements(self) -> list[RequirementRef]:
        return self.required_fields

    @property
    def resolved_requirements(self) -> list[RequirementRef]:
        return self.resolved_fields

    @property
    def gateway_category(self) -> str | None:
        if self.intent_gateway is None:
            return None
        return self.intent_gateway.category

    @property
    def gateway_message_role(self) -> MessageRole | None:
        if self.intent_gateway is None:
            return None
        return self.intent_gateway.message_role

    @property
    def gateway_extraction_required(self) -> bool | None:
        if self.intent_gateway is None:
            return None
        return self.intent_gateway.extraction_required
