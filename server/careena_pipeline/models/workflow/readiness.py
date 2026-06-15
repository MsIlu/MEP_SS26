from pydantic import Field

from careena_pipeline.models.common.base import PipelineModel


class AssessmentReadiness(PipelineModel):
    ready: bool = False
    missing_information: list[str] = Field(default_factory=list)
    reason_tags: list[str] = Field(default_factory=list)
    blocking_requirements: list[str] = Field(default_factory=list)
    confidence_gaps: list[str] = Field(default_factory=list)
    disambiguation_needed: bool = False
    confirmation_needed: bool = False
