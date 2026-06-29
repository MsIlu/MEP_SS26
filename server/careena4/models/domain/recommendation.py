from pydantic import Field

from careena4.models.common import PipelineModel, RecommendationReadiness
from careena4.models.workflow.recommendation_result import RecommendationResult


class RecommendationState(PipelineModel):
    readiness: RecommendationReadiness = "not_ready"
    blocking_followup_ids: list[str] = Field(default_factory=list)
    recommendation_allowed: bool = False
    recommendation_result: RecommendationResult | None = None
