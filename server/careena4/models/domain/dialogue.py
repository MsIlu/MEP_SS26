from typing import Literal
from uuid import uuid4

from pydantic import Field

from careena4.models.common import (
    ConversationPhase,
    FollowupPriority,
    FollowupReason,
    PipelineModel,
    QuestionIntent,
    QuestionKind,
    SubjectScope,
)
from careena4.models.domain.guided_input import GuidedInputContract


class FollowupNeed(PipelineModel):
    followup_id: str = Field(default_factory=lambda: str(uuid4()))
    observation_id: str | None = None
    reason: FollowupReason
    person_relation: SubjectScope | None = None
    priority: FollowupPriority = "medium"
    blocking: bool = False
    resolved: bool = False


class SafetyQuestionContext(PipelineModel):
    """Stores the traceable safety context for one active safety clarification."""

    question_code: str = "raw_red_flag_clarification"
    source_stage: Literal["raw_message", "structured_claim", "case_slice"] = "raw_message"

    # Evidence that caused the clarification.
    evidence_terms: list[str] = Field(default_factory=list)
    evidence_observation_ids: list[str] = Field(default_factory=list)

    # Catalog provenance for medical traceability.
    source_system: str = "STS"
    source_version: str | None = None
    consultation_reason_source_id: str | None = None
    consultation_reason_key: str | None = None
    consultation_reason_label_de: str | None = None
    criterion_key: str | None = None
    criterion_label_de: str | None = None
    criterion_role: str | None = None
    urgency_effect: str | None = None
    careena_decision_role: str | None = None
    catalog_mapping_status: str = "unmapped"
    matched_lay_term: str | None = None

    # Reserved for the later red-flag lifecycle model.
    related_safety_event_id: str | None = None


class ActiveQuestion(PipelineModel):
    question_id: str = Field(default_factory=lambda: str(uuid4()))
    kind: QuestionKind
    question_intent: QuestionIntent
    target_observation_id: str | None = None
    target_followup_id: str | None = None
    prompt_text: str
    blocking: bool = False
    allows_additional_medical_info: bool = True
    guided_input: GuidedInputContract | None = None
    reply_suggestions: list[str] = Field(default_factory=list)

    # Compatibility bridge for existing resolver/response code.
    # New safety-specific metadata belongs in safety_context.
    safety_question_code: str | None = None
    safety_evidence_terms: list[str] = Field(default_factory=list)
    safety_context: SafetyQuestionContext | None = None


class ConversationState(PipelineModel):
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    phase: ConversationPhase = "intake"
    active_question: ActiveQuestion | None = None
    followup_needs: list[FollowupNeed] = Field(default_factory=list)
