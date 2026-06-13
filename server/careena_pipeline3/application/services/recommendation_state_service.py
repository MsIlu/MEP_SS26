from careena_pipeline3.application.services.readiness_evaluator import (
    AssessmentReadinessEvaluator,
)
from careena_pipeline3.models.domain import ConcernState, DialogueState, MedicalCase
from careena_pipeline3.models.turn import (
    EntryDecision,
    ReadinessStateUpdate,
    RecommendationGateDecision,
)


class RecommendationStateService:
    """
    Owns the active post-processing next-step policy plus legacy
    recommendation hooks.

    `allowed_next_step` is the active steering truth after processing and
    before response selection.
    `recommendation_requested` and `recommendation_ready` remain visible as
    legacy / future recommendation hooks.
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
        concern_state: ConcernState | None = None,
        entry_decision: EntryDecision | None = None,
        person_reference_present: bool = False,
        multi_person_context: bool = False,
        subject_relation_unclear: bool = False,
    ) -> ReadinessStateUpdate:
        readiness = self.readiness_evaluator.evaluate(
            medical_case,
            dialogue_state=dialogue_state,
            person_reference_present=person_reference_present,
            multi_person_context=multi_person_context,
            subject_relation_unclear=subject_relation_unclear,
        )
        gate_decision = self._build_gate_decision(
            dialogue_state=dialogue_state,
            concern_state=concern_state,
            readiness=readiness,
            entry_decision=entry_decision,
        )
        # Legacy recommendation hook; no longer the primary next-step driver.
        dialogue_state.recommendation_ready = (
            readiness.ready
            and readiness.has_medical_problem
            and not readiness.blocking_requirements
            and gate_decision.allowed_next_step == "allow_recommendation"
        )
        return ReadinessStateUpdate(
            dialogue_state=dialogue_state,
            assessment_readiness=readiness,
            pending_followup=dialogue_state.pending_followup,
            gate_decision=gate_decision,
        )

    @staticmethod
    def _build_gate_decision(
        *,
        dialogue_state: DialogueState,
        concern_state: ConcernState | None,
        readiness,
        entry_decision: EntryDecision | None,
    ) -> RecommendationGateDecision:
        active_transition_kind = (
            dialogue_state.pending_dialogue_transition.kind
            if dialogue_state.pending_dialogue_transition is not None
            else None
        )
        if entry_decision is not None and entry_decision.response_mode_hint == "out_of_scope":
            return RecommendationGateDecision(
                gate_status="out_of_scope",
                allowed_next_step="out_of_scope",
                active_transition_kind=active_transition_kind,
                reason_tags=["gate:out_of_scope", *readiness.reason_tags],
            )

        if (
            entry_decision is not None
            and entry_decision.dialogue_transition_action == "request_recommendation"
        ):
            return RecommendationGateDecision(
                gate_status="recommendation_allowed",
                allowed_next_step="allow_recommendation",
                active_transition_kind=active_transition_kind,
                reason_tags=["policy:request_recommendation", *readiness.reason_tags],
            )

        if (
            entry_decision is not None
            and entry_decision.dialogue_transition_action == "report_more_information"
        ):
            return RecommendationGateDecision(
                gate_status="return_to_medical",
                allowed_next_step="return_to_medical",
                active_transition_kind=active_transition_kind,
                reason_tags=["policy:return_to_medical", *readiness.reason_tags],
            )

        if dialogue_state.pending_followup is not None:
            return RecommendationGateDecision(
                gate_status="concern_clarification",
                allowed_next_step="ask_clarifying_question",
                active_transition_kind=active_transition_kind,
                reason_tags=["gate:pending_followup", *readiness.reason_tags],
            )

        if active_transition_kind == "recommendation_ready_check":
            return RecommendationGateDecision(
                gate_status="closing_check",
                allowed_next_step="stay_on_closing_check",
                active_transition_kind=active_transition_kind,
                reason_tags=["policy:closing_check", *readiness.reason_tags],
            )

        concern_phase = concern_state.phase if concern_state is not None else None
        return RecommendationGateDecision(
            gate_status=(
                "medical_exploration"
                if readiness.has_medical_problem
                else "missing_medical_problem"
            ),
            allowed_next_step="continue_medical",
            active_transition_kind=active_transition_kind,
            reason_tags=[
                f"gate:concern_phase:{concern_phase or 'none'}",
                *readiness.reason_tags,
            ],
        )
