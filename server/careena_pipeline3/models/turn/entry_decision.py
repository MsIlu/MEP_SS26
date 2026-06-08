from pydantic import Field

from careena_pipeline3.models.common import (
    Call2OperationMode,
    Call2Task,
    MessageRole,
    PipelineModel,
)


class EntryDecision(PipelineModel):
    extraction_required: bool = False
    recommendation_requested: bool = False
    response_mode_hint: str | None = None
    message_role: MessageRole = "new_information"
    person_reference_present: bool = False
    multi_person_context: bool = False
    subject_relation_unclear: bool = False
    active_modules: list[str] = Field(default_factory=list)
    call2_tasks: list[Call2Task] = Field(default_factory=list)
    call2_operation_mode: Call2OperationMode = "focused_new_fact_extraction"
    trace_notes: list[str] = Field(default_factory=list)
