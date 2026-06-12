from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.extraction import ExtractionResult
from careena_pipeline3.models.turn.case_update_bridge import CaseUpdateBridge


class ExtractionPayload(PipelineModel):
    """
    Transitional extraction output consumed by turn orchestration.

    The long-term target is not this full payload shape. For the current
    boundary-first stage it carries only the neighboring extraction outputs
    that orchestration and case truth still read directly, while the heavier
    `case_update_bridge` remains available for the case-truth edge.
    """

    extracted_fields: dict[str, object] = Field(default_factory=dict)
    active_modules: list[str] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)
    extraction_result: ExtractionResult | None = None
    case_update_bridge: CaseUpdateBridge | None = None
