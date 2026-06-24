from pydantic import Field

from careena4.models.common import ObservationStatus, ObservationType, PipelineModel, SubjectScope
from careena4.models.domain import Source


class ExtractedPersonInput(PipelineModel):
    relation: SubjectScope
    relation_source: Source | None = None


class ExtractedObservationInput(PipelineModel):
    type: ObservationType
    label: str
    label_source: Source | None = None
    status: ObservationStatus = "active"
    status_source: Source | None = None
    person_ref: SubjectScope | None = None
    person_ref_source: Source | None = None
    onset: str | None = None
    onset_source: Source | None = None
    body_site: str | None = None
    body_site_source: Source | None = None
    description: str | None = None
    description_source: Source | None = None
    severity: int | str | None = None
    severity_source: Source | None = None
    mechanism: str | None = None
    mechanism_source: Source | None = None
    functional_limitation: str | None = None
    functional_limitation_source: Source | None = None
    measurement_kind: str | None = None
    measurement_kind_source: Source | None = None

    @property
    def source_span(self) -> str | None:
        for source in (
            self.label_source,
            self.status_source,
            self.person_ref_source,
            self.onset_source,
            self.body_site_source,
            self.description_source,
            self.severity_source,
            self.mechanism_source,
            self.functional_limitation_source,
            self.measurement_kind_source,
        ):
            if source is not None and source.source_span not in (None, ""):
                return source.source_span
        return None


class ExtractedCaseInput(PipelineModel):
    topic_signal: str | None = None
    topic_source: Source | None = None
    person: ExtractedPersonInput | None = None
    observations: list[ExtractedObservationInput] = Field(default_factory=list)


# Transitional aliases while direct callers are moved onto the new names.
ObservationClaim = ExtractedObservationInput
ExtractionClaims = ExtractedCaseInput
