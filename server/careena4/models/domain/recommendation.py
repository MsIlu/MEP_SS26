from pydantic import Field

from careena4.models.common import PipelineModel, RecommendationReadiness
from careena4.models.workflow.recommendation_result import RecommendationResult


class RecommendationState(PipelineModel):
    request_present: bool = False
    readiness: RecommendationReadiness = "not_ready"
    blocking_followup_ids: list[str] = Field(default_factory=list)
    recommendation_allowed: bool = False
    closing_prompt_active: bool = False
    recommendation_result: RecommendationResult | None = None
