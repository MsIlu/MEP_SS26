from __future__ import annotations

from pydantic import Field

from careena4.models.common import PipelineModel


class ExtractedSymptomCandidate(PipelineModel):
    """
    One symptom understood from the current user message.

    This is current-turn understanding only. It is not durable MedicalCase truth
    and it is not a triage decision.
    """

    source_label: str
    is_medical: bool = True
    normalized_label_de: str | None = None
    clinical_term_de: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning_note: str | None = None

    @property
    def chip_label(self) -> str:
        """Return the best user-visible label for a symptom chip."""

        return (self.normalized_label_de or self.source_label).strip()


class StsConsultationReasonCandidate(PipelineModel):
    """
    One possible STS consultation reason for the current user message.

    STS levels are source metadata only. They are not a final Careena
    recommendation or urgency decision.
    """

    sts_id: str
    sts_label_de: str | None = None
    source_category_de: str | None = None
    source_sts_levels_present: list[int] = Field(default_factory=list)
    match_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    match_reason: str | None = None


class CurrentTurnUnderstanding(PipelineModel):
    """
    What MedGemma understood from the current user message.

    This model separates current message understanding from MedicalCase truth,
    DialogueState and derived recommendation/safety decisions.
    """

    raw_message: str
    symptoms: list[ExtractedSymptomCandidate] = Field(default_factory=list)
    sts_matches: list[StsConsultationReasonCandidate] = Field(default_factory=list)
    no_match_reason: str | None = None
    trace_notes: list[str] = Field(default_factory=list)

    def symptom_labels(self) -> list[str]:
        """Return deduplicated user-visible symptom labels."""

        labels: list[str] = []
        seen: set[str] = set()

        for symptom in self.symptoms:
            if not symptom.is_medical:
                continue

            label = symptom.chip_label
            if not label:
                continue

            identity = label.casefold().strip()
            if identity in seen:
                continue

            seen.add(identity)
            labels.append(label)

        return labels
