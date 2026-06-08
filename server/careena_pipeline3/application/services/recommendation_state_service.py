from careena_pipeline3.application.services.readiness_evaluator import (
    AssessmentReadinessEvaluator,
)
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.workflow import AssessmentReadiness


class RecommendationStateService:
    """
    Owns recommendation request/readiness state, not recommendation content.

    `recommendation_requested` represents explicit user intent.
    `recommendation_ready` represents architectural eligibility based on the
    current information state.
    """

    def __init__(
        self,
        *,
        readiness_evaluator: AssessmentReadinessEvaluator | None = None,
    ):
        self.readiness_evaluator = readiness_evaluator or AssessmentReadinessEvaluator()

    def sync_dialogue_state(
        self,
        *,
        dialogue_state: DialogueState,
        medical_case: MedicalCase | None,
        person_reference_present: bool = False,
        multi_person_context: bool = False,
        subject_relation_unclear: bool = False,
    ) -> tuple[DialogueState, AssessmentReadiness]:
        readiness = self.readiness_evaluator.evaluate(
            medical_case,
            dialogue_state=dialogue_state,
            person_reference_present=person_reference_present,
            multi_person_context=multi_person_context,
            subject_relation_unclear=subject_relation_unclear,
        )
        dialogue_state.recommendation_ready = (
            readiness.ready
            and readiness.has_medical_problem
            and not readiness.blocking_requirements
        )
        return dialogue_state, readiness
