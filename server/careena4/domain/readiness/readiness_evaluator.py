from careena4.models.domain import CaseTopic, ConversationState, MedicalCase, RecommendationState
from careena4.models.workflow import AssessmentReadiness


class ReadinessEvaluator:
    def evaluate(
        self,
        *,
        case_topic: CaseTopic | None,
        medical_case: MedicalCase | None,
        conversation_state: ConversationState,
    ) -> RecommendationState:
        if medical_case is None or not medical_case.active_observations():
            return RecommendationState(
                request_present=conversation_state.recommendation_requested,
                readiness="not_ready",
                blocking_followup_ids=[],
                recommendation_allowed=False,
                closing_prompt_active=False,
            )
        blocking_followup_ids = [
            need.followup_id
            for need in conversation_state.followup_needs
            if need.blocking and not need.resolved
        ]
        central_observations = medical_case.central_observations()
        ready = bool(
            case_topic is not None
            and central_observations
            and not blocking_followup_ids
            and (
                conversation_state.active_question is None
                or not conversation_state.active_question.blocking
            )
        )
        return RecommendationState(
            request_present=conversation_state.recommendation_requested,
            readiness="ready" if ready else ("tentative" if central_observations else "not_ready"),
            blocking_followup_ids=blocking_followup_ids,
            recommendation_allowed=ready,
            closing_prompt_active=(
                conversation_state.active_question is not None
                and conversation_state.active_question.kind == "closing_choice"
            ),
        )


class AssessmentReadinessBuilder:
    def build(
        self,
        *,
        case_topic: CaseTopic | None,
        medical_case: MedicalCase | None,
        conversation_state: ConversationState,
        recommendation_state: RecommendationState,
    ) -> AssessmentReadiness:
        if medical_case is None or not medical_case.active_observations():
            return AssessmentReadiness(
                ready=False,
                has_medical_problem=False,
                missing_information=["main_complaint"],
                blocking_requirements=["main_complaint"],
                reason_tags=["no_main_medical_problem"],
            )
        if recommendation_state.blocking_followup_ids:
            return AssessmentReadiness(
                ready=False,
                has_medical_problem=True,
                missing_information=["followup_needed"],
                blocking_requirements=list(recommendation_state.blocking_followup_ids),
                reason_tags=["blocking_followup_present"],
            )
        return AssessmentReadiness(
            ready=recommendation_state.recommendation_allowed and case_topic is not None,
            has_medical_problem=True,
            reason_tags=["minimum_information_present"] if case_topic is not None else ["missing_topic"],
        )
