from careena4.models.common import PipelineModel


class Source(PipelineModel):
    message_id: str | None = None
    source_span: str | None = None


class Provenance(Source):
    source: str = "user_message"
    confidence: float | None = None
