from pydantic import Field

from careena4.models.common import CareLevel, PipelineModel, Specialty, Urgency, UrgencyAssessment


class RecommendationResult(PipelineModel):
    allowed: bool = False
    summary: str | None = None
    urgency: Urgency = "unknown"
    urgency_level: UrgencyAssessment = "unclear"
    care_level: CareLevel = "unknown"
    specialty: Specialty = "unknown"
    reasons: list[str] = Field(default_factory=list)
    next_step: str | None = None
    limitations: list[str] = Field(default_factory=list)
    # Human-readable provenance: which data the recommendation actually drew on
    # (e.g. "Chat-Verlauf", "Symptom-Tagebuch (3 Einträge)", "Medikamentenplan").
    # Computed deterministically, never by the LLM, so it stays trustworthy.
    data_sources: list[str] = Field(default_factory=list)
