from careena_pipeline.llm.routing_advisor import LLMRoutingAdvisor
from careena_pipeline.routing.fallback_engine import RecommendationEngine


class RecommendationStep:
    """Builds the final routing recommendation once planning allows it."""

    def __init__(
        self,
        *,
        recommendation_engine: RecommendationEngine,
        routing_advisor: LLMRoutingAdvisor | None = None,
    ):
        self.recommendation_engine = recommendation_engine
        self.routing_advisor = routing_advisor

    def recommend(self, *, case, safety, gate):
        if self.routing_advisor is None:
            return self.recommendation_engine.recommend(case)

        return self.routing_advisor.recommend(
            case=case,
            safety=safety,
            gate=gate,
        )
