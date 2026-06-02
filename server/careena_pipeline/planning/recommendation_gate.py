from careena_pipeline.models import (
    AssessmentReadiness,
    RecommendationGateDecision,
)
from careena_pipeline.pipeline_rules import FOLLOWUP_QUESTIONS, question_for_slot
from careena_pipeline.state.module_registry import followup_slot_for_requirement


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

        if readiness.disambiguation_needed:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["disambiguation_needed"],
                question=question,
                missing_information=missing_information,
                activated_modules=list(readiness.recommended_modules),
            )

        if readiness.blocking_requirements:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["blocking_requirements"],
                question=question,
                missing_information=readiness.blocking_requirements,
                activated_modules=list(readiness.recommended_modules),
            )

        if readiness.missing_information:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["missing_information"],
                question=question,
                missing_information=readiness.missing_information,
                activated_modules=list(readiness.recommended_modules),
            )

        if readiness.confirmation_needed:
            return RecommendationGateDecision(
                action="confirm_information",
                reasons=["confirmation_needed"],
                missing_information=[],
                activated_modules=list(readiness.recommended_modules),
            )

        return RecommendationGateDecision(
            action="recommend",
            reasons=["ready_requested" if user_requests_recommendation else "ready"],
            missing_information=[],
            can_recommend_with_uncertainty=bool(readiness.confidence_gaps),
            activated_modules=list(readiness.recommended_modules),
        )


def _question_for(requirement: str) -> str:
    normalized = followup_slot_for_requirement(requirement) or requirement
    return FOLLOWUP_QUESTIONS.get(normalized, question_for_slot(normalized))
