from typing import Literal

from pydantic import Field

from careena_pipeline3.models.common import PipelineModel


RequirementFollowupStatus = Literal["resolved", "invalid_answer", "unclear"]
RequirementFollowupTargetKind = Literal["observation", "subject"]


class RequirementFieldUpdate(PipelineModel):
    requirement_key: str
    slot: str
    target_kind: RequirementFollowupTargetKind
    target_observation_id: str | None = None
    normalized_value: str | int
    source_text: str


class RequirementFollowupResolutionResult(PipelineModel):
    status: RequirementFollowupStatus
    requirement_key: str
    slot: str
    normalized_value: str | int | None = None
    rejection_reason: str | None = None
    contains_extra_medical_information: bool = False
    trace_notes: list[str] = Field(default_factory=list)
