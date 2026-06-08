from pydantic import Field

from careena_pipeline3.models.common import PipelineModel


class SafetyState(PipelineModel):
    checked_sources: list[str] = Field(default_factory=list)
    red_flag_detected: bool = False
    severity: str | None = None
    action: str | None = None
    trace_notes: list[str] = Field(default_factory=list)
