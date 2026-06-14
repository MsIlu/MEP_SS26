from pydantic import Field

from careena_pipeline3.models.common import (
    Call2OperationMode,
    Call2Task,
    MessageRole,
    PipelineModel,
)
from careena_pipeline3.models.domain import ConcernRelation, ConcernTurnRole


class EntryDecision(PipelineModel):
    extraction_required: bool = False
    recommendation_requested: bool = False
    response_mode_hint: str | None = None
    message_role: MessageRole = "new_information"
    call2_profile: str = "default"
    additional_medical_information: bool = False
    clear_pending_choice_prompt: bool = False
    choice_prompt_action: str | None = None
    person_reference_present: bool = False
    multi_person_context: bool = False
    subject_relation_unclear: bool = False
    concern_relation: ConcernRelation = "unclear"
    latest_turn_role: ConcernTurnRole = "unclear"
    active_modules: list[str] = Field(default_factory=list)
    call2_tasks: list[Call2Task] = Field(default_factory=list)
    call2_operation_mode: Call2OperationMode = "focused_new_fact_extraction"
    trace_notes: list[str] = Field(default_factory=list)
