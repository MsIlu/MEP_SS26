from pydantic import Field

from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import PlannerModule, RecommendationGateAction


class RecommendationGateDecision(PipelineModel):
    action: RecommendationGateAction
    question: str | None = None
    reasons: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    can_recommend_with_uncertainty: bool = False
    activated_modules: list[PlannerModule] = Field(default_factory=list)
