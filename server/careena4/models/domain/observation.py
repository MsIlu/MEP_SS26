from __future__ import annotations

from uuid import uuid4

from pydantic import Field

from careena4.models.common import (
    ObservationStatus,
    ObservationType,
    PipelineModel,
    SubjectScope,
)
from careena4.models.domain.source import Source


class Observation(PipelineModel):
    observation_id: str = Field(default_factory=lambda: str(uuid4()))
    type: ObservationType
    status: ObservationStatus = "active"
    status_source: Source | None = None
    person_ref: SubjectScope = "unclear"
    person_ref_source: Source | None = None
    normalized_label_de: str
    normalized_label_source: Source | None = None
    clinical_term_de: str | None = None
    clinical_term_source: Source | None = None
    onset: str | None = None
    onset_source: Source | None = None
    body_site: str | None = None
    body_site_source: Source | None = None
    description: str | None = None
    description_sources: list[Source] = Field(default_factory=list)
    severity: int | str | None = None
    severity_source: Source | None = None

    def identity_key(self) -> tuple[str, str | None, SubjectScope]:
        return (
            self.type,
            self.normalized_label_de.casefold(),
            self.person_ref,
        )

    def is_negated(self) -> bool:
        return self.status == "negated"

    def is_active(self) -> bool:
        return self.status in {"active", "reported", "enriched", "corrected"}

    def is_central(self) -> bool:
        return self.type == "symptom"

    def merge_from(self, *, other: Observation) -> None:
        if other.status == "negated":
            self.status = "negated"
            if other.status_source is not None:
                self.status_source = other.status_source.model_copy(deep=True)
        elif not self.is_negated():
            self.status = "active"
            if other.status_source is not None:
                self.status_source = other.status_source.model_copy(deep=True)
        if other.person_ref != "unclear":
            self.person_ref = other.person_ref
            if other.person_ref_source is not None:
                self.person_ref_source = other.person_ref_source.model_copy(deep=True)
        self._merge_optional_field(
            "clinical_term_de",
            "clinical_term_source",
            other.clinical_term_de,
            other.clinical_term_source,
        )
        self._merge_optional_field("onset", "onset_source", other.onset, other.onset_source)
        self._merge_optional_field("body_site", "body_site_source", other.body_site, other.body_site_source)
        self._merge_optional_field("severity", "severity_source", other.severity, other.severity_source)
        if other.description not in (None, ""):
            self.description = other.description
            if other.description_sources:
                self.description_sources = [source.model_copy(deep=True) for source in other.description_sources]

    def matches_identity(self, *, other: Observation) -> bool:
        return self.identity_key() == other.identity_key()

    def has_same_medical_content(self, *, other: Observation) -> bool:
        return (
            self.status == other.status
            and self.person_ref == other.person_ref
            and self.onset == other.onset
            and self.body_site == other.body_site
            and self.description == other.description
            and self.severity == other.severity
        )

    def _merge_optional_field(
        self,
        field_name: str,
        source_field_name: str,
        value: object,
        source: Source | None,
    ) -> None:
        if value in (None, "", []):
            return
        setattr(self, field_name, value)
        if source is not None:
            setattr(self, source_field_name, source.model_copy(deep=True))
