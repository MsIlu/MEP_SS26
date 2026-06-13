from __future__ import annotations

from careena_pipeline3.models.domain import ConcernState, DialogueState, MedicalCase
from careena_pipeline3.models.turn import EntryDecision, RecommendationGateDecision
from careena_pipeline3.models.workflow import AssessmentReadiness


class ConcernStateService:
    """
    Role:
    - owns the small concern-layer continuity contract for a turn.

    Input contract:
    - existing concern state plus optional canonical medical case truth

    Output contract:
    - returns a concern state that is at least initialized and whose
      observation links still point at currently active case observations

    Does not decide:
    - recommendation readiness
    - response policy
    - medical case truth
    - concern summary inference

    Transitional:
    - yes; this service currently normalizes and preserves state without
      pretending the full concern semantics are already modeled
    """

    def ensure_state(
        self,
        concern_state: ConcernState | None,
    ) -> ConcernState:
        return concern_state if concern_state is not None else ConcernState()

    def sync_after_entry(
        self,
        *,
        concern_state: ConcernState,
        entry_decision: EntryDecision,
        dialogue_state: DialogueState,
    ) -> tuple[ConcernState, list[str]]:
        trace_notes: list[str] = []
        closing_node = (
            dialogue_state.pending_dialogue_transition.kind
            if dialogue_state.pending_dialogue_transition is not None
            else None
        )
        if concern_state.active_closing_node != closing_node:
            concern_state.active_closing_node = closing_node
            trace_notes.append(
                "concern_state:active_closing_node:"
                f"{closing_node or 'none'}"
            )

        if closing_node is not None:
            concern_state.phase = "closing_check"
            trace_notes.append("concern_state:phase:closing_check")

        return concern_state, trace_notes

    def sync_after_case_update(
        self,
        *,
        concern_state: ConcernState,
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState,
    ) -> tuple[ConcernState, list[str]]:
        trace_notes: list[str] = []
        if medical_case is None or not concern_state.linked_observation_ids:
            filtered_ids = concern_state.linked_observation_ids
        else:
            valid_ids = {
                observation.id for observation in medical_case.active_observations()
            }
            filtered_ids = [
                observation_id
                for observation_id in concern_state.linked_observation_ids
                if observation_id in valid_ids
            ]
            if filtered_ids != concern_state.linked_observation_ids:
                concern_state.linked_observation_ids = filtered_ids
                trace_notes.append("concern_state:pruned_missing_observation_links")

        if medical_case is not None:
            medical_case.ensure_primary_problem()
            active_concern_id = medical_case.primary_problem_id
            if concern_state.active_concern_id != active_concern_id:
                concern_state.active_concern_id = active_concern_id
                trace_notes.append(
                    "concern_state:active_concern_id:"
                    f"{active_concern_id or 'none'}"
                )
            summary = medical_case.current_case_frame_label()
            if summary != concern_state.summary:
                concern_state.summary = summary
                if summary is not None:
                    trace_notes.append("concern_state:summary_from_case_frame")

        closing_node = (
            dialogue_state.pending_dialogue_transition.kind
            if dialogue_state.pending_dialogue_transition is not None
            else None
        )
        concern_state.active_closing_node = closing_node
        if closing_node is not None:
            concern_state.phase = "closing_check"
        elif dialogue_state.pending_followup is not None:
            concern_state.phase = "clarification"
        elif concern_state.active_concern_id is not None:
            concern_state.phase = "exploration"

        return concern_state, trace_notes

    def sync_after_gate(
        self,
        *,
        concern_state: ConcernState,
        readiness: AssessmentReadiness,
        gate_decision: RecommendationGateDecision,
    ) -> tuple[ConcernState, list[str]]:
        if not readiness.has_medical_problem:
            concern_state.information_sufficiency = "insufficient"
        elif readiness.ready and not readiness.blocking_requirements:
            concern_state.information_sufficiency = "sufficient"
        else:
            concern_state.information_sufficiency = "tentative"

        if gate_decision.allowed_next_step == "ask_clarifying_question":
            concern_state.phase = "clarification"
        elif gate_decision.allowed_next_step == "safety_question":
            concern_state.phase = "clarification"
        elif gate_decision.allowed_next_step == "out_of_scope":
            concern_state.phase = "clarification"
        elif gate_decision.allowed_next_step == "stay_on_closing_check":
            concern_state.phase = "closing_check"
        elif gate_decision.allowed_next_step == "allow_recommendation":
            concern_state.phase = "recommendation_gate"
        elif gate_decision.allowed_next_step == "continue_medical":
            concern_state.phase = "exploration"
        elif gate_decision.allowed_next_step == "return_to_medical":
            concern_state.phase = "exploration"

        return concern_state, [
            f"concern_state:phase:{concern_state.phase}",
            (
                "concern_state:next_step:"
                f"{gate_decision.allowed_next_step}"
            ),
            (
                "concern_state:information_sufficiency:"
                f"{concern_state.information_sufficiency}"
            ),
        ]
