from careena_pipeline3.domain import RequirementPolicy
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.workflow import AssessmentReadiness


class AssessmentReadinessEvaluator:
    """
    Conservative readiness check derived from canonical case truth.

    It only answers whether minimum required information is present. It does
    not own question wording or recommendation policy.
    """

    def __init__(self, *, requirement_policy: RequirementPolicy | None = None):
        self.requirement_policy = requirement_policy or RequirementPolicy()

    def evaluate(
        self,
        medical_case: MedicalCase | None,
        *,
        dialogue_state: DialogueState | None = None,
        person_reference_present: bool = False,
        multi_person_context: bool = False,
        subject_relation_unclear: bool = False,
    ) -> AssessmentReadiness:
        if medical_case is None:
            return AssessmentReadiness(
                ready=False,
                has_medical_problem=False,
                missing_information=["main_complaint"],
                blocking_requirements=["main_complaint"],
                reason_tags=["no_case_state"],
            )

        medical_case.ensure_primary_problem()
        state = dialogue_state or DialogueState()
        complaint_observations = medical_case.complaint_observations()
        diagnosis_observations = medical_case.observations_of_type("diagnosis")
        has_medical_problem = bool(complaint_observations or diagnosis_observations)

        resolved_requirements = self.requirement_policy.resolved_requirements(
            medical_case=medical_case,
            dialogue_state=state,
        )
        open_requirements = list(state.open_requirements)
        if not open_requirements:
            open_requirements = self.requirement_policy.has_blocking_requirements(
                medical_case=medical_case,
                dialogue_state=state,
                active_modules=state.active_modules,
                person_reference_present=person_reference_present,
                multi_person_context=multi_person_context,
                subject_relation_unclear=subject_relation_unclear,
            )

        disambiguation_needed = self.requirement_policy.needs_subject_resolution(
            medical_case,
            person_reference_present=person_reference_present,
            multi_person_context=multi_person_context,
            subject_relation_unclear=subject_relation_unclear,
        )

        if not has_medical_problem:
            return AssessmentReadiness(
                ready=False,
                has_medical_problem=False,
                missing_information=["main_complaint"],
                blocking_requirements=["main_complaint"],
                reason_tags=["no_main_medical_problem"],
                disambiguation_needed=False,
            )

        if open_requirements:
            return AssessmentReadiness(
                ready=False,
                has_medical_problem=True,
                missing_information=open_requirements,
                blocking_requirements=open_requirements,
                reason_tags=["missing_information"],
                disambiguation_needed=disambiguation_needed,
            )

        return AssessmentReadiness(
            ready=True,
            has_medical_problem=True,
            reason_tags=["minimum_information_present"],
            disambiguation_needed=disambiguation_needed,
        )
