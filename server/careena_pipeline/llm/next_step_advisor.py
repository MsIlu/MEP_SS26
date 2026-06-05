import json
import logging

from careena_pipeline.llm.call_control import (
    CallModelConfig,
    NEXT_STEP_CALL,
)
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
    Optional support call for follow-up shaping within gate bounds.

    The primary direction comes from readiness plus the deterministic gate.
    This helper should only refine hard-to-hardcode follow-up decisions, not
    replace the main Call 1 / Call 2 / Call 3 contract.
    """

    def __init__(
        self,
        engine: ExtractionEngine,
        recommendation_gate: RecommendationGate | None = None,
        call_models: CallModelConfig | None = None,
    ):
        self.engine = engine
        self.recommendation_gate = recommendation_gate or RecommendationGate()
        self.call_models = call_models

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
        deterministic_gate = self.recommendation_gate.normalize(
            readiness=readiness,
            decision=self.recommendation_gate.decide(
                readiness=readiness,
                user_requests_recommendation=user_requests_recommendation,
            ),
            user_requests_recommendation=user_requests_recommendation,
        )
        support_modules = _select_support_modules(
            message_update=message_update,
            deterministic_gate=deterministic_gate,
        )
        payload = {
            "last_user_message": last_user_message,
            "user_requests_recommendation": user_requests_recommendation,
            "safety": safety.model_dump(),
            "readiness_heuristic": readiness.model_dump(),
            "deterministic_gate": deterministic_gate.model_dump(),
            "case": case.model_dump(),
            "dialogue_state": dialogue_state.model_dump() if dialogue_state is not None else None,
            "message_update": message_update.model_dump() if message_update is not None else None,
            "activated_modules": support_modules,
        }

        try:
            llm_result = self.engine.extract(
                text=json.dumps(payload, ensure_ascii=False),
                system_prompt=build_next_step_system_prompt(support_modules),
                output_schema=LLMNextStepResult,
                max_tokens=1200,
                model=(
                    self.call_models.model_for(NEXT_STEP_CALL)
                    if self.call_models is not None
                    else None
                ),
            )
        except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError) as exc:
            logger.warning(
                "LLM next-step decision failed; falling back to deterministic gate: %s",
                exc,
            )
            return deterministic_gate

        return RecommendationGateDecision(
            action=llm_result.action,
            question=llm_result.question,
            reasons=llm_result.reasons,
            missing_information=llm_result.missing_information,
            can_recommend_with_uncertainty=llm_result.can_recommend_with_uncertainty,
            activated_modules=llm_result.activated_modules or support_modules,
        )


def _select_support_modules(
    *,
    message_update: MessageUpdate | None,
    deterministic_gate: RecommendationGateDecision,
) -> list[str]:
    modules: list[str] = []
    if message_update is not None:
        modules.extend(message_update.planner_hints.recommended_modules)
    modules.extend(deterministic_gate.activated_modules)

    seen: set[str] = set()
    return [module for module in modules if not (module in seen or seen.add(module))]
