from pydantic import Field

from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import CareLevel, Specialty, Urgency, UrgencyAssessment


class Recommendation(PipelineModel):
    care_level: CareLevel = "unknown"
    urgency_level: UrgencyAssessment = "unclear"
    specialty: Specialty = "unknown"
    urgency: Urgency = "unknown"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning_tags: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    explanation: str | None = None
