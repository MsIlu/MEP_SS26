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
        expected_action = _expected_action_for(readiness)
        missing_information = readiness.blocking_requirements or readiness.missing_information
        question = _question_for(missing_information[0]) if missing_information else None
        activated_modules = _activated_modules(
            action=expected_action,
            readiness=readiness,
            user_requests_recommendation=user_requests_recommendation,
        )

        if expected_action == "ask_followup" and readiness.disambiguation_needed:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["disambiguation_needed"],
                question=_disambiguation_question(missing_information, fallback_question=question),
                missing_information=missing_information,
                activated_modules=activated_modules,
            )

        if expected_action == "ask_followup" and readiness.blocking_requirements:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["blocking_requirements"],
                question=question,
                missing_information=readiness.blocking_requirements,
                activated_modules=activated_modules,
            )

        if expected_action == "ask_followup" and readiness.missing_information:
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=["missing_information"],
                question=question,
                missing_information=readiness.missing_information,
                activated_modules=activated_modules,
            )

        if expected_action == "confirm_information":
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

    def normalize(
        self,
        *,
        readiness: AssessmentReadiness,
        decision: RecommendationGateDecision,
        user_requests_recommendation: bool = False,
    ) -> RecommendationGateDecision:
        expected_action = _expected_action_for(readiness)
        missing_information = readiness.blocking_requirements or readiness.missing_information
        activated_modules = decision.activated_modules or _activated_modules(
            action=expected_action,
            readiness=readiness,
            user_requests_recommendation=user_requests_recommendation,
        )
        reasons = decision.reasons or _default_reasons_for(
            action=expected_action,
            readiness=readiness,
            user_requests_recommendation=user_requests_recommendation,
        )

        if expected_action == "ask_followup":
            question = decision.question or (
                _disambiguation_question(missing_information)
                if readiness.disambiguation_needed
                else (_question_for(missing_information[0]) if missing_information else None)
            )
            return RecommendationGateDecision(
                action="ask_followup",
                reasons=reasons,
                question=question,
                missing_information=missing_information,
                can_recommend_with_uncertainty=False,
                activated_modules=activated_modules,
            )

        if expected_action == "confirm_information":
            return RecommendationGateDecision(
                action="confirm_information",
                reasons=reasons,
                question=None,
                missing_information=[],
                can_recommend_with_uncertainty=False,
                activated_modules=activated_modules,
            )

        return RecommendationGateDecision(
            action="recommend",
            reasons=reasons,
            question=None,
            missing_information=[],
            can_recommend_with_uncertainty=bool(readiness.confidence_gaps),
            activated_modules=activated_modules,
        )


def _question_for(requirement: str) -> str:
    normalized = normalized_followup_slot(requirement) or requirement
    return FOLLOWUP_QUESTIONS.get(normalized, question_for_slot(normalized))


def _disambiguation_question(
    missing_information: list[str],
    *,
    fallback_question: str | None = None,
) -> str:
    if "subject.subject_relation" in set(missing_information):
        return (
            "Geht es um Sie selbst oder um eine andere Person? "
            "Wenn es um mehrere Personen geht, sagen Sie bitte auch klar, wer welche Beschwerden hat."
        )
    return fallback_question or (
        "Damit ich die Beschwerden richtig zuordnen kann: "
        "Wer hat welche Beschwerden, und was gehoert zu wem?"
    )


def _expected_action_for(readiness: AssessmentReadiness) -> str:
    if readiness.disambiguation_needed:
        return "ask_followup"
    if readiness.blocking_requirements:
        return "ask_followup"
    if readiness.missing_information:
        return "ask_followup"
    if readiness.confirmation_needed:
        return "confirm_information"
    return "recommend"


def _default_reasons_for(
    *,
    action: str,
    readiness: AssessmentReadiness,
    user_requests_recommendation: bool,
) -> list[str]:
    if action == "ask_followup":
        if readiness.disambiguation_needed:
            return ["disambiguation_needed"]
        if readiness.blocking_requirements:
            return ["blocking_requirements"]
        return ["missing_information"]
    if action == "confirm_information":
        return ["confirmation_needed"]
    return ["ready_requested" if user_requests_recommendation else "ready"]


def _activated_modules(
    *,
    action: str,
    readiness: AssessmentReadiness,
    user_requests_recommendation: bool,
) -> list[str]:
    modules: list[str] = []
    if action == "ask_followup" and readiness.disambiguation_needed:
        modules.append("topic_disambiguation")
    if action == "ask_followup" and (readiness.blocking_requirements or readiness.missing_information):
        modules.extend(["requirement_resolution", "single_followup_generation"])
    if action == "confirm_information":
        modules.append("confirmation_check")
    if action == "recommend":
        modules.extend(["recommendation_readiness", "routing_recommendation"])
        if user_requests_recommendation:
            modules.append("recommendation_requested")

    seen: set[str] = set()
    return [module for module in modules if not (module in seen or seen.add(module))]
