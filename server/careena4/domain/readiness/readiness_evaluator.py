from careena4.domain.case import CaseManager
from careena4.models.domain import ConversationState, MedicalCase, RecommendationState
from careena4.models.workflow import AssessmentReadiness


class ReadinessEvaluator:
    def __init__(self, *, case_manager: CaseManager | None = None) -> None:
        self.case_manager = case_manager or CaseManager()

    def evaluate(
        self,
        *,
        medical_case: MedicalCase | None,
        conversation_state: ConversationState,
    ) -> RecommendationState:
        if medical_case is None or not self.case_manager.has_active_observations(medical_case=medical_case):
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
        central_observations = self.case_manager.central_observations(medical_case=medical_case)
        has_topic = self.case_manager.has_topic(medical_case=medical_case)
        ready = bool(
            has_topic
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
    def __init__(self, *, case_manager: CaseManager | None = None) -> None:
        self.case_manager = case_manager or CaseManager()

    def build(
        self,
        *,
        medical_case: MedicalCase | None,
        conversation_state: ConversationState,
        recommendation_state: RecommendationState,
    ) -> AssessmentReadiness:
        if medical_case is None or not self.case_manager.has_active_observations(medical_case=medical_case):
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
        has_topic = self.case_manager.has_topic(medical_case=medical_case)
        return AssessmentReadiness(
            ready=recommendation_state.recommendation_allowed and has_topic,
            has_medical_problem=True,
            reason_tags=["minimum_information_present"] if has_topic else ["missing_topic"],
        )
