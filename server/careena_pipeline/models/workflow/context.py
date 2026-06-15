from pydantic import Field

from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import DialogueTopicStatus, PlannerModule
from careena_pipeline.models.domain.dialogue import StagedFollowupAnswer
from careena_pipeline.models.workflow.intent_gateway import IntentGateway


class ConversationTurn(PipelineModel):
    role: str
    content: str


class CaseSummaryObservation(PipelineModel):
    type: str
    display_label: str
    concept: str | None = None
    body_site: str | None = None
    temporality: str | None = None
    severity: int | None = None
    details: dict[str, str] = Field(default_factory=dict)
    status: str | None = None


class CaseSummary(PipelineModel):
    subject_relation: str = "unknown"
    subject_age: int | None = None
    primary_focus: str | None = None
    primary_problem_id: str | None = None
    active_problem_ids: list[str] = Field(default_factory=list)
    observations: list[CaseSummaryObservation] = Field(default_factory=list)


class DialogueSummary(PipelineModel):
    current_topic_status: DialogueTopicStatus = "single_topic"
    last_question_key: str | None = None
    active_modules: list[str] = Field(default_factory=list)
    open_requirements: list[str] = Field(default_factory=list)
    pending_followup: str | None = None
    staged_followup_answers: list[StagedFollowupAnswer] = Field(default_factory=list)
    awaiting_confirmation: bool = False
    recommendation_requested: bool = False
    recommended_modules: list[PlannerModule] = Field(default_factory=list)


class CaseUpdateContext(PipelineModel):
    latest_user_message: str
    pending_slot: str | None = None
    last_assistant_question: str | None = None
    recent_turns: list[ConversationTurn] = Field(default_factory=list)
    intent_gateway: IntentGateway | None = None
    case_summary: CaseSummary | None = None
    dialogue_summary: DialogueSummary | None = None
