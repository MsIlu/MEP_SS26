from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.domain import ConcernState, DialogueState, MedicalCase
from careena_pipeline3.models.workflow import RecommendationResult


class TurnResult(PipelineModel):
    """
    Boundary output contract for one completed turn.

    Field groups:
    - persisted truth to write back:
      `medical_case`, `dialogue_state`, `concern_state`
    - output:
      `response_mode`, `response_text`, `recommendation_result`
    - observability:
      `trace_notes`
    """

    response_mode: str
    response_text: str
    medical_case: MedicalCase | None = None
    dialogue_state: DialogueState
    concern_state: ConcernState
    recommendation_result: RecommendationResult | None = None
    trace_notes: list[str] = Field(default_factory=list)
