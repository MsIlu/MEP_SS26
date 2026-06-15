from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.extraction import ExtractionResult
from careena_pipeline3.models.turn.case_update_bridge import CaseUpdateBridge


class ExtractionPayload(PipelineModel):
    """
    Extraction output consumed by turn orchestration.

    The active runtime path is centered on the explicit truth-edge bridge.
    `extraction_result` remains available only as a diagnostic compatibility
    artifact for logging and tests.
    """

    extracted_fields: dict[str, object] = Field(default_factory=dict)
    active_modules: list[str] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)
    extraction_result: ExtractionResult | None = None
    case_update_bridge: CaseUpdateBridge | None = None
