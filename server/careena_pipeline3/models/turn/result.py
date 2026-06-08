from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.turn.context import TurnContext
from careena_pipeline3.models.workflow import RecommendationResult


class TurnResult(PipelineModel):
    response_mode: str
    context: TurnContext
    response_text: str | None = None
    recommendation_result: RecommendationResult | None = None
