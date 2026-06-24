from __future__ import annotations

from uuid import uuid4

from pydantic import Field

from careena4.models.common import (
    ObservationStatus,
    ObservationType,
    PipelineModel,
    SubjectScope,
)
from careena4.models.domain.provenance import Source


class Observation(PipelineModel):
    observation_id: str = Field(default_factory=lambda: str(uuid4()))
    type: ObservationType
    status: ObservationStatus = "active"
    status_source: Source | None = None
    person_ref: SubjectScope = "unclear"
    person_ref_source: Source | None = None
    label: str
    label_source: Source | None = None
    onset: str | None = None
    onset_source: Source | None = None
    body_site: str | None = None
    body_site_source: Source | None = None
    description: str | None = None
    description_sources: list[Source] = Field(default_factory=list)
    severity: int | str | None = None
    severity_source: Source | None = None
    mechanism: str | None = None
    mechanism_source: Source | None = None
    functional_limitation: str | None = None
    functional_limitation_source: Source | None = None
    measurement_kind: str | None = None
    measurement_kind_source: Source | None = None

    def identity_key(self) -> tuple[str, str | None, SubjectScope]:
        return (
            self.type,
            self.label.casefold(),
            self.person_ref,
        )

    def get_attribute(self, key: str) -> object | None:
        return self.attributes.get(key)

    def is_negated(self) -> bool:
        return self.status == "negated"

    def is_active(self) -> bool:
        return self.status in {"active", "reported", "enriched", "corrected"}

    def is_central(self) -> bool:
        return self.type in {"symptom", "injury", "measurement"}

    @property
    def normalized_concept(self) -> str:
        return self.label.casefold()

    @property
    def subject_ref(self) -> SubjectScope:
        return self.person_ref

    @subject_ref.setter
    def subject_ref(self, relation: SubjectScope) -> None:
        self.person_ref = relation

    @property
    def negated(self) -> bool:
        return self.is_negated()

    @negated.setter
    def negated(self, negated: bool) -> None:
        if negated:
            self.status = "negated"
        elif self.status == "negated":
            self.status = "active"

    @property
    def topic_relation(self) -> str:
        return "central" if self.is_central() else "related"

    @property
    def attributes(self) -> dict[str, object]:
        attributes: dict[str, object] = {}
        if self.onset not in (None, ""):
            attributes["duration_or_onset"] = self.onset
        if self.body_site not in (None, ""):
            attributes["body_site"] = self.body_site
        if self.description not in (None, ""):
            attributes["description"] = self.description
        if self.severity not in (None, ""):
            attributes["severity"] = self.severity
        if self.mechanism not in (None, ""):
            attributes["mechanism"] = self.mechanism
        if self.functional_limitation not in (None, ""):
            attributes["functional_limitation"] = self.functional_limitation
        if self.measurement_kind not in (None, ""):
            attributes["kind"] = self.measurement_kind
        return attributes

    @attributes.setter
    def attributes(self, attributes: dict[str, object]) -> None:
        self.onset = None
        self.body_site = None
        self.description = None
        self.description_sources = []
        self.severity = None
        self.mechanism = None
        self.functional_limitation = None
        self.measurement_kind = None
        self.apply_legacy_attributes(attributes=attributes)

    @property
    def provenance(self) -> list[Source]:
        sources: list[Source] = []
        for candidate in (
            self.label_source,
            self.status_source,
            self.person_ref_source,
            self.onset_source,
            self.body_site_source,
            self.severity_source,
            self.mechanism_source,
            self.functional_limitation_source,
            self.measurement_kind_source,
            *self.description_sources,
        ):
            if candidate is None:
                continue
            if candidate not in sources:
                sources.append(candidate)
        return sources

    def apply_legacy_attributes(
        self,
        *,
        attributes: dict[str, object],
        source: Source | None = None,
    ) -> None:
        if "duration_or_onset" in attributes or "onset" in attributes:
            value = attributes.get("duration_or_onset", attributes.get("onset"))
            self.onset = self._clean_text(value)
            if source is not None and self.onset is not None:
                self.onset_source = source.model_copy(deep=True)
        if "body_site" in attributes:
            self.body_site = self._clean_text(attributes.get("body_site"))
            if source is not None and self.body_site is not None:
                self.body_site_source = source.model_copy(deep=True)
        if "description" in attributes:
            self.description = self._clean_text(attributes.get("description"))
            if source is not None and self.description is not None:
                self.description_sources = [source.model_copy(deep=True)]
        if "severity" in attributes:
            self.severity = self._clean_scalar(attributes.get("severity"))
            if source is not None and self.severity not in (None, ""):
                self.severity_source = source.model_copy(deep=True)
        if "mechanism" in attributes:
            self.mechanism = self._clean_text(attributes.get("mechanism"))
            if source is not None and self.mechanism is not None:
                self.mechanism_source = source.model_copy(deep=True)
        if "functional_limitation" in attributes:
            self.functional_limitation = self._clean_text(attributes.get("functional_limitation"))
            if source is not None and self.functional_limitation is not None:
                self.functional_limitation_source = source.model_copy(deep=True)
        if "kind" in attributes:
            self.measurement_kind = self._clean_text(attributes.get("kind"))
            if source is not None and self.measurement_kind is not None:
                self.measurement_kind_source = source.model_copy(deep=True)

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
        self._merge_optional_field("onset", "onset_source", other.onset, other.onset_source)
        self._merge_optional_field("body_site", "body_site_source", other.body_site, other.body_site_source)
        self._merge_optional_field("severity", "severity_source", other.severity, other.severity_source)
        self._merge_optional_field("mechanism", "mechanism_source", other.mechanism, other.mechanism_source)
        self._merge_optional_field(
            "functional_limitation",
            "functional_limitation_source",
            other.functional_limitation,
            other.functional_limitation_source,
        )
        self._merge_optional_field(
            "measurement_kind",
            "measurement_kind_source",
            other.measurement_kind,
            other.measurement_kind_source,
        )
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
            and self.mechanism == other.mechanism
            and self.functional_limitation == other.functional_limitation
            and self.measurement_kind == other.measurement_kind
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

    @staticmethod
    def _clean_text(value: object) -> str | None:
        if value in (None, "", []):
            return None
        return str(value).strip()

    @staticmethod
    def _clean_scalar(value: object) -> int | str | None:
        if value in (None, "", []):
            return None
        return value  # type: ignore[return-value]
