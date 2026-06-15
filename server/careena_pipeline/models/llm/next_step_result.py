from pydantic import Field

from careena_pipeline.models.common.types import PlannerModule, RecommendationGateAction
from careena_pipeline.models.system.baseSchema import BaseSchema


class LLMNextStepResult(BaseSchema):
    action: RecommendationGateAction
    question: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    can_recommend_with_uncertainty: bool = False
    activated_modules: list[PlannerModule] = Field(default_factory=list)
