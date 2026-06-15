from dataclasses import dataclass

from pydantic import Field

from careena_pipeline.state.module_registry import ModuleName, RequirementRef
from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import (
    MessageRole,
    PlannerModule,
)
from careena_pipeline.models.domain.dialogue import StagedFollowupAnswer
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


@dataclass(frozen=True)
class MessageIntentSignals:
    intent_category: str | None
    is_medical: bool
    extraction_required: bool
    intent_confidence: float
    message_role: MessageRole
    possible_new_topic: bool

    @property
    def has_signals(self) -> bool:
        return any(
            (
                self.intent_category is not None,
                self.is_medical,
                self.extraction_required,
                self.intent_confidence > 0.0,
                self.message_role != "new_information",
                self.possible_new_topic,
            )
        )


@dataclass(frozen=True)
class MessageTraceSignals:
    notes: list[str]
    intent_gateway: IntentGateway | None
    llm_intent_category: str | None
    llm_is_medical: bool | None
    llm_extraction_required: bool | None
    llm_message_role: MessageRole | None

    @property
    def has_signals(self) -> bool:
        return any(
            (
                bool(self.notes),
                self.intent_gateway is not None,
                self.llm_intent_category is not None,
                self.llm_is_medical is not None,
                self.llm_extraction_required is not None,
                self.llm_message_role is not None,
            )
        )


@dataclass(frozen=True)
class MessageStagingHints:
    staged_followup_answers: list[StagedFollowupAnswer]
    clear_staged_followup_answers: bool

    @property
    def has_signals(self) -> bool:
        return self.clear_staged_followup_answers or bool(self.staged_followup_answers)


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
    staged_followup_answers: list[StagedFollowupAnswer] = Field(default_factory=list)
    clear_staged_followup_answers: bool = False

    @classmethod
    def from_parts(
        cls,
        *,
        raw_text: str,
        case_payload: MessageCasePayload | None = None,
        intent_signals: MessageIntentSignals | None = None,
        requirement_hints: MessageRequirementHints | None = None,
        planner_hints: MessagePlannerHints | None = None,
        trace_signals: MessageTraceSignals | None = None,
        staging_hints: MessageStagingHints | None = None,
    ) -> "MessageUpdate":
        case_payload = case_payload or MessageCasePayload(
            subject=None,
            observations_added=[],
            negated_observations_added=[],
        )
        intent_signals = intent_signals or MessageIntentSignals(
            intent_category=None,
            is_medical=False,
            extraction_required=False,
            intent_confidence=0.0,
            message_role="new_information",
            possible_new_topic=False,
        )
        requirement_hints = requirement_hints or MessageRequirementHints(
            active_modules=[],
            required_fields=[],
            resolved_fields=[],
        )
        planner_hints = planner_hints or MessagePlannerHints(
            recommended_modules=[],
            recommendation_requested=False,
        )
        trace_signals = trace_signals or MessageTraceSignals(
            notes=[],
            intent_gateway=None,
            llm_intent_category=None,
            llm_is_medical=None,
            llm_extraction_required=None,
            llm_message_role=None,
        )
        staging_hints = staging_hints or MessageStagingHints(
            staged_followup_answers=[],
            clear_staged_followup_answers=False,
        )

        return cls(
            raw_text=raw_text,
            intent_category=intent_signals.intent_category,
            is_medical=intent_signals.is_medical,
            extraction_required=intent_signals.extraction_required,
            intent_confidence=intent_signals.intent_confidence,
            subject=case_payload.subject,
            observations_added=list(case_payload.observations_added),
            negated_observations_added=list(case_payload.negated_observations_added),
            user_requests_recommendation=planner_hints.recommendation_requested,
            possible_new_topic=intent_signals.possible_new_topic,
            notes=list(trace_signals.notes),
            message_role=intent_signals.message_role,
            intent_gateway=trace_signals.intent_gateway,
            llm_intent_category=trace_signals.llm_intent_category,
            llm_is_medical=trace_signals.llm_is_medical,
            llm_extraction_required=trace_signals.llm_extraction_required,
            llm_message_role=trace_signals.llm_message_role,
            active_modules=list(requirement_hints.active_modules),
            required_fields=list(requirement_hints.required_fields),
            resolved_fields=list(requirement_hints.resolved_fields),
            recommended_modules=list(planner_hints.recommended_modules),
            staged_followup_answers=list(staging_hints.staged_followup_answers),
            clear_staged_followup_answers=staging_hints.clear_staged_followup_answers,
        )

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
    def intent_signals(self) -> MessageIntentSignals:
        return MessageIntentSignals(
            intent_category=self.intent_category,
            is_medical=self.is_medical,
            extraction_required=self.extraction_required,
            intent_confidence=self.intent_confidence,
            message_role=self.message_role,
            possible_new_topic=self.possible_new_topic,
        )

    @property
    def trace_signals(self) -> MessageTraceSignals:
        return MessageTraceSignals(
            notes=list(self.notes),
            intent_gateway=self.intent_gateway,
            llm_intent_category=self.llm_intent_category,
            llm_is_medical=self.llm_is_medical,
            llm_extraction_required=self.llm_extraction_required,
            llm_message_role=self.llm_message_role,
        )

    @property
    def staging_hints(self) -> MessageStagingHints:
        return MessageStagingHints(
            staged_followup_answers=list(self.staged_followup_answers),
            clear_staged_followup_answers=self.clear_staged_followup_answers,
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
