from careena_pipeline.models import (
    AssessmentReadiness,
    RecommendationGateDecision,
)


class RecommendationGate:
    """
    Decides whether the pipeline may produce a recommendation now.

    It separates process control from both readiness heuristics and the actual
    recommendation engine.
    """

    def decide(
        self,
        *,
        case,
        readiness: AssessmentReadiness,
        user_requests_recommendation: bool = False,
    ) -> RecommendationGateDecision:
        case.ensure_primary_problem()
        if readiness.disambiguation_needed:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["disambiguation_needed"],
                missing_information=readiness.blocking_requirements or readiness.missing_information,
            )

        if readiness.blocking_requirements:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["blocking_requirements"],
                missing_information=readiness.blocking_requirements,
            )

        if readiness.missing_information:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["missing_information"],
                missing_information=readiness.missing_information,
            )

        if readiness.confirmation_needed:
            return RecommendationGateDecision(
                action="confirm_information",
                reasons=["confirmation_needed"],
                missing_information=[],
            )

        return RecommendationGateDecision(
            action="recommend",
            reasons=["ready"],
            missing_information=[],
            can_recommend_with_uncertainty=bool(readiness.confidence_gaps),
        )
