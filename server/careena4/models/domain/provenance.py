from careena4.models.common import PipelineModel


class Provenance(PipelineModel):
    source: str = "user_message"
    source_span: str | None = None
    confidence: float | None = None
