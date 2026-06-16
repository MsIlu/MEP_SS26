from pydantic import Field

from careena4.models.common import PipelineModel


class CaseIssue(PipelineModel):
    kind: str
    focus_observation_id: str | None = None
    incoming_observation_label: str | None = None
    incoming_observation_type: str | None = None
    note: str | None = None
    status: str = "active"
    trace_notes: list[str] = Field(default_factory=list)
