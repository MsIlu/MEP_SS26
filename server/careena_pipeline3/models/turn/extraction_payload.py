from pydantic import Field

from careena_pipeline3.models.common import PipelineModel, PlannerModule
from careena_pipeline3.models.extraction import ExtractionResult
from careena_pipeline3.models.turn.message_delta import MessageDelta


class ExtractionPayload(PipelineModel):
    """
    Transitional extraction output consumed by turn orchestration.

    The long-term target is not this full payload shape. For the current
    boundary-first stage it exposes the small orchestration signals that the
    `DialogueManager` should read directly, while the heavier
    `message_delta` bridge remains available for the case-truth edge.
    """

    extracted_fields: dict[str, object] = Field(default_factory=dict)
    active_modules: list[str] = Field(default_factory=list)
    recommendation_requested: bool = False
    recommended_modules: list[PlannerModule] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)
    extraction_result: ExtractionResult | None = None
    message_delta: MessageDelta | None = None
