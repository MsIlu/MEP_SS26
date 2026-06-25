from uuid import uuid4

from pydantic import Field

from careena4.models.common import (
    ObservationStatus,
    ObservationType,
    PipelineModel,
    SubjectScope,
    TopicRelation,
)
from careena4.models.domain.provenance import Provenance


class Observation(PipelineModel):
    observation_id: str = Field(default_factory=lambda: str(uuid4()))
    type: ObservationType
    label: str
    normalized_concept: str | None = None
    subject_ref: SubjectScope = "unclear"
    negated: bool = False
    status: ObservationStatus = "reported"
    topic_relation: TopicRelation = "unclear"
    attributes: dict[str, object] = Field(default_factory=dict)
    provenance: list[Provenance] = Field(default_factory=list)

    def identity_key(self) -> tuple[str, str | None, SubjectScope]:
        return (
            self.type,
            self.normalized_concept or self.label.casefold(),
            self.subject_ref,
        )

    def get_attribute(self, key: str) -> object | None:
        return self.attributes.get(key)
