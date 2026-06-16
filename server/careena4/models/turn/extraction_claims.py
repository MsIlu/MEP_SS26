from pydantic import Field

from careena4.models.common import ObservationType, PipelineModel, SubjectScope


class ObservationClaim(PipelineModel):
    type: ObservationType
    label: str
    normalized_concept: str | None = None
    subject_ref: SubjectScope | None = None
    negated: bool = False
    attributes: dict[str, object] = Field(default_factory=dict)
    source_span: str | None = None


class ExtractionClaims(PipelineModel):
    topic_signal: str | None = None
    subject_claims: dict[str, object] = Field(default_factory=dict)
    observations: list[ObservationClaim] = Field(default_factory=list)
