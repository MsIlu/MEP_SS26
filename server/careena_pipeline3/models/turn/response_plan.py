from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.workflow import RecommendationResult


class ResponsePlan(PipelineModel):
    response_mode: str
    response_text: str | None = None
    recommendation_result: RecommendationResult | None = None
    trace_notes: list[str] = Field(default_factory=list)
