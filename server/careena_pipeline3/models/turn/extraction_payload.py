from pydantic import Field

from careena_pipeline3.models.extraction import ExtractionResult
from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.turn.message_delta import MessageDelta


class ExtractionPayload(PipelineModel):
    extracted_fields: dict[str, object] = Field(default_factory=dict)
    active_modules: list[str] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)
    extraction_result: ExtractionResult | None = None
    message_delta: MessageDelta | None = None
