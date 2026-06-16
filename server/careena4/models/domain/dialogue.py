from uuid import uuid4

from pydantic import Field

from careena4.models.common import (
    CaseExtensionKind,
    ConversationPhase,
    FollowupPriority,
    FollowupReason,
    OffTopicState,
    PipelineModel,
    QuestionIntent,
    QuestionKind,
    SubjectScope,
    TopicFitState,
)
from careena4.models.domain.guided_input import GuidedInputContract


class FollowupNeed(PipelineModel):
    followup_id: str = Field(default_factory=lambda: str(uuid4()))
    observation_id: str | None = None
    reason: FollowupReason
    target_extension_kind: CaseExtensionKind | None = None
    case_focus_label: str | None = None
    related_observation_ids: list[str] = Field(default_factory=list)
    priority: FollowupPriority = "medium"
    blocking: bool = False
    resolved: bool = False


class ActiveQuestion(PipelineModel):
    question_id: str = Field(default_factory=lambda: str(uuid4()))
    kind: QuestionKind
    question_intent: QuestionIntent
    target_observation_id: str | None = None
    target_followup_id: str | None = None
    target_subject_scope: SubjectScope | None = None
    prompt_text: str
    blocking: bool = False
    allows_additional_medical_info: bool = True
    guided_input: GuidedInputContract | None = None
    safety_question_code: str | None = None
    safety_evidence_terms: list[str] = Field(default_factory=list)


class ConversationState(PipelineModel):
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    phase: ConversationPhase = "intake"
    active_question: ActiveQuestion | None = None
    followup_needs: list[FollowupNeed] = Field(default_factory=list)
    recommendation_requested: bool = False
    off_topic_state: OffTopicState = "none"
    topic_fit_state: TopicFitState = "unclear"
