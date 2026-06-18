from __future__ import annotations

from pydantic import ConfigDict, Field

from careena4.models.common import PipelineModel


class MedGemmaSymptomMappingCandidate(PipelineModel):
    """
    One MedGemma-produced terminology mapping candidate.

    This is a terminology candidate only. It is not a diagnosis, not a final
    medical truth and not a triage decision.
    """

    source_label: str
    is_medical: bool = True
    normalized_label_de: str | None = None
    clinical_term_de: str | None = None
    snomed_code: str | None = None
    snomed_display_de: str | None = None
    mapping_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    validation_status: str = "candidate"
    reasoning_note: str | None = None

    model_config = ConfigDict(extra="forbid")


class MedGemmaSymptomMappingOutput(PipelineModel):
    """
    Structured MedGemma output for symptom terminology mapping.

    The provider accepts multiple candidates and chooses the best medical one.
    """

    candidates: list[MedGemmaSymptomMappingCandidate] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")
