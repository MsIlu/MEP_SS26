from uuid import uuid4

from pydantic import Field

from careena_pipeline.state.module_registry import ModuleName, RequirementRef
from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import (
    DialogueTopicStatus,
    PlannerModule,
)


class StagedFollowupAnswer(PipelineModel):
    requirement_key: str
    raw_text: str
    slot: str | None = None
    focus_observation_id: str | None = None


class DialogueState(PipelineModel):
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    active_case_id: str | None = None
    current_topic_status: DialogueTopicStatus = "single_topic"
    last_question_key: str | None = None
    active_modules: list[ModuleName] = Field(default_factory=list)
    open_requirements: list[RequirementRef] = Field(default_factory=list)
    resolved_requirements: list[RequirementRef] = Field(default_factory=list)
    pending_followup: RequirementRef | None = None
    staged_followup_answers: list[StagedFollowupAnswer] = Field(default_factory=list)
    awaiting_confirmation: bool = False
    recommendation_requested: bool = False
    recommended_modules: list[PlannerModule] = Field(default_factory=list)
    focus_observation_id: str | None = None
    focus_label: str | None = None
