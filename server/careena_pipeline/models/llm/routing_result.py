from pydantic import Field

from careena_pipeline.models.common.types import CareLevel, Specialty, Urgency, UrgencyAssessment
from careena_pipeline.models.system.baseSchema import BaseSchema


class LLMRoutingResult(BaseSchema):
    care_level: CareLevel
    urgency_level: UrgencyAssessment
    specialty: Specialty = "unknown"
    urgency: Urgency = "unknown"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning_tags: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    explanation: str | None = None
