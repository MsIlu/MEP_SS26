from pydantic import Field

from careena4.models.common import ObservationStatus, PipelineModel, SubjectScope
from careena4.models.domain import Observation, Person, Source


class _LegacyCaseWritePayload(PipelineModel):
    person_update: Person | None = None
    observations: list[Observation] = Field(default_factory=list)


class _ObservationPatch(PipelineModel):
    status: ObservationStatus | None = None
    person_ref: SubjectScope | None = None
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

    def has_updates(self) -> bool:
        return bool(self.model_fields_set)
