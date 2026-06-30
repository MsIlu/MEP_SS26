from pydantic import Field

from careena4.models.common import ObservationStatus, ObservationType, PipelineModel, SubjectScope
from careena4.models.domain import Source


class ExtractedPersonInput(PipelineModel):
    relation: SubjectScope
    relation_source: Source | None = None
    age: int | None = None
    age_source: Source | None = None
    sex: str | None = None
    sex_source: Source | None = None


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
        ):
            if source is not None and source.source_span not in (None, ""):
                return source.source_span
        return None

class ExtractedCaseInput(PipelineModel):
    topic_label: str | None = None
    topic_description: str | None = None
    person: ExtractedPersonInput | None = None
    observations: list[ExtractedObservationInput] = Field(default_factory=list)

    def has_topic_update(self) -> bool:
        return (self.topic_label or "").strip() != "" or (self.topic_description or "").strip() != ""

    def has_content(self) -> bool:
        return self.has_topic_update() or self.has_meaningful_person_update() or bool(self.observations)

    def has_meaningful_person_update(self) -> bool:
        if self.person is None:
            return False
        return (
            self.person.relation in {"self", "child", "other"}
            or self.person.age is not None
            or self.person.sex not in (None, "")
        )
