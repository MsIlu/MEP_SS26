import json
import logging

from careena_pipeline.planning.recommendation_gate import RecommendationGate
from careena_pipeline.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline.core.engine import ExtractionEngine
from careena_pipeline.models import (
    AssessmentReadiness,
    DialogueState,
    MedicalCase,
    MessageUpdate,
    RecommendationGateDecision,
    SafetyResult,
)
from careena_pipeline.models.llm.next_step_result import LLMNextStepResult
from careena_pipeline.llm.prompts.next_step import build_next_step_system_prompt


logger = logging.getLogger("careena_pipeline")


class LLMNextStepAdvisor:
    """
    Uses an LLM for the hard-to-hardcode conversation-control decision:
    ask a focused follow-up, ask for confirmation, or proceed to recommendation.
    """

    def __init__(
        self,
        engine: ExtractionEngine,
        recommendation_gate: RecommendationGate | None = None,
    ):
        self.engine = engine
        self.recommendation_gate = recommendation_gate or RecommendationGate()

    def decide(
        self,
        *,
        case: MedicalCase,
        dialogue_state: DialogueState | None,
        message_update: MessageUpdate | None,
        safety: SafetyResult,
        readiness: AssessmentReadiness,
        last_user_message: str,
        user_requests_recommendation: bool = False,
    ) -> RecommendationGateDecision:
        module_names = _select_next_step_modules(
            message_update=message_update,
            readiness=readiness,
            user_requests_recommendation=user_requests_recommendation,
        )
        payload = {
            "last_user_message": last_user_message,
            "user_requests_recommendation": user_requests_recommendation,
            "safety": safety.model_dump(),
            "readiness_heuristic": readiness.model_dump(),
            "case": case.model_dump(),
            "dialogue_state": dialogue_state.model_dump() if dialogue_state is not None else None,
            "message_update": message_update.model_dump() if message_update is not None else None,
            "activated_modules": module_names,
        }

        try:
            llm_result = self.engine.extract(
                text=json.dumps(payload, ensure_ascii=False),
                system_prompt=build_next_step_system_prompt(module_names),
                output_schema=LLMNextStepResult,
                max_tokens=1200,
            )
        except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError) as exc:
            logger.warning(
                "LLM next-step decision failed; falling back to deterministic gate: %s",
                exc,
            )
            decision = self.recommendation_gate.decide(
                readiness=readiness,
                user_requests_recommendation=user_requests_recommendation,
            )
            decision.activated_modules = module_names
            return decision

        return RecommendationGateDecision(
            action=llm_result.action,
            question=llm_result.question,
            reasons=llm_result.reasons,
            missing_information=llm_result.missing_information,
            can_recommend_with_uncertainty=llm_result.can_recommend_with_uncertainty,
            activated_modules=llm_result.activated_modules or module_names,
        )


def _select_next_step_modules(
    *,
    message_update: MessageUpdate | None,
    readiness: AssessmentReadiness,
    user_requests_recommendation: bool,
) -> list[str]:
    modules: list[str] = []
    if message_update is not None:
        modules.extend(message_update.recommended_modules)

    if readiness.recommended_modules:
        modules.extend(readiness.recommended_modules)

    if readiness.disambiguation_needed:
        modules.append("topic_disambiguation")

    if readiness.blocking_requirements or readiness.missing_information:
        modules.extend(
            [
                "requirement_resolution",
                "single_followup_generation",
            ]
        )

    if readiness.confirmation_needed:
        modules.append("confirmation_check")

    if readiness.ready or user_requests_recommendation:
        modules.extend(
            [
                "recommendation_readiness",
                "routing_recommendation",
            ]
        )

    seen: set[str] = set()
    return [module for module in modules if not (module in seen or seen.add(module))]
