import json
import logging

from careena_pipeline.llm.call_control import (
    CallModelConfig,
    ROUTING_CALL,
)
from careena_pipeline.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline.core.engine import ExtractionEngine
from careena_pipeline.models import (
    MedicalCase,
    Recommendation,
    RecommendationGateDecision,
    SafetyResult,
)
from careena_pipeline.models.llm.routing_result import LLMRoutingResult
from careena_pipeline.llm.prompts.routing import ROUTING_SYSTEM_PROMPT
from careena_pipeline.routing.fallback_engine import RecommendationEngine
from careena_pipeline.routing import (
    apply_case_based_routing_safety,
    build_reasons,
    normalize_confidence,
)


logger = logging.getLogger("careena_pipeline")


class LLMRoutingAdvisor:
    """
    Primary Call 3 that produces the structured routing recommendation.

    The advisor owns only the LLM routing call and maps the validated output into
    the internal Recommendation model. Fallbacks and reason text are delegated to
    smaller routing helpers.
    """

    def __init__(
        self,
        engine: ExtractionEngine,
        fallback_engine: RecommendationEngine | None = None,
        call_models: CallModelConfig | None = None,
    ):
        self.engine = engine
        self.fallback_engine = fallback_engine or RecommendationEngine()
        self.call_models = call_models

    def recommend(
        self,
        *,
        case: MedicalCase,
        safety: SafetyResult,
        gate: RecommendationGateDecision,
    ) -> Recommendation:
        payload = {
            "safety": safety.model_dump(),
            "recommendation_gate": gate.model_dump(),
            "case": case.model_dump(),
        }

        try:
            llm_result = self.engine.extract(
                text=json.dumps(payload, ensure_ascii=False),
                system_prompt=ROUTING_SYSTEM_PROMPT,
                output_schema=LLMRoutingResult,
                max_tokens=1400,
                model=(
                    self.call_models.model_for(ROUTING_CALL)
                    if self.call_models is not None
                    else None
                ),
            )
        except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError) as exc:
            logger.warning(
                "LLM routing failed; falling back to deterministic recommendation: %s",
                exc,
            )
            fallback = self.fallback_engine.recommend(case)
            fallback.reasoning_tags.append("llm_routing_failed")
            fallback = apply_case_based_routing_safety(case, fallback)
            fallback.reasons = build_reasons(case, fallback)
            return fallback

        recommendation = Recommendation(
            care_level=llm_result.care_level,
            urgency_level=llm_result.urgency_level,
            specialty=llm_result.specialty,
            urgency=llm_result.urgency,
            confidence=normalize_confidence(llm_result.confidence),
            reasoning_tags=llm_result.reasoning_tags,
            explanation=llm_result.explanation,
        )
        recommendation = apply_case_based_routing_safety(case, recommendation)
        recommendation.reasons = build_reasons(case, recommendation)
        return recommendation
