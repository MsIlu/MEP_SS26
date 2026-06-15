from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.common.types import ProvenanceSource


class Provenance(PipelineModel):
    source: ProvenanceSource
    message_id: str | None = None
    source_span: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    note: str | None = None
