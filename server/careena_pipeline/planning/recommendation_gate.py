from careena_pipeline.models import (
    AssessmentReadiness,
    RecommendationGateDecision,
)
from careena_pipeline.planning.requirement_state import normalized_followup_slot
from careena_pipeline.pipeline_rules import FOLLOWUP_QUESTIONS, question_for_slot


class RecommendationGate:
    """
    Decides the deterministic next step from readiness information.

    It separates process control from both readiness heuristics and the actual
    recommendation engine.
    """

    def decide(
        self,
        *,
        readiness: AssessmentReadiness,
        user_requests_recommendation: bool = False,
    ) -> RecommendationGateDecision:
        missing_information = readiness.blocking_requirements or readiness.missing_information
        question = _question_for(missing_information[0]) if missing_information else None
        activated_modules = _activated_modules(
            readiness=readiness,
            user_requests_recommendation=user_requests_recommendation,
        )

        if readiness.disambiguation_needed:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["disambiguation_needed"],
                question=question,
                missing_information=missing_information,
                activated_modules=activated_modules,
            )

        if readiness.blocking_requirements:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["blocking_requirements"],
                question=question,
                missing_information=readiness.blocking_requirements,
                activated_modules=activated_modules,
            )

        if readiness.missing_information:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["missing_information"],
                question=question,
                missing_information=readiness.missing_information,
                activated_modules=activated_modules,
            )

        if readiness.confirmation_needed:
            return RecommendationGateDecision(
                action="confirm_information",
                reasons=["confirmation_needed"],
                missing_information=[],
                activated_modules=activated_modules,
            )

        return RecommendationGateDecision(
            action="recommend",
            reasons=["ready_requested" if user_requests_recommendation else "ready"],
            missing_information=[],
            can_recommend_with_uncertainty=bool(readiness.confidence_gaps),
            activated_modules=activated_modules,
        )


def _question_for(requirement: str) -> str:
    normalized = normalized_followup_slot(requirement) or requirement
    return FOLLOWUP_QUESTIONS.get(normalized, question_for_slot(normalized))


def _activated_modules(
    *,
    readiness: AssessmentReadiness,
    user_requests_recommendation: bool,
) -> list[str]:
    modules: list[str] = []
    if readiness.disambiguation_needed:
        modules.append("topic_disambiguation")
    if readiness.blocking_requirements or readiness.missing_information:
        modules.extend(["requirement_resolution", "single_followup_generation"])
    if readiness.confirmation_needed:
        modules.append("confirmation_check")
    if readiness.ready or user_requests_recommendation:
        modules.extend(["recommendation_readiness", "routing_recommendation"])

    seen: set[str] = set()
    return [module for module in modules if not (module in seen or seen.add(module))]
