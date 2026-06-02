from careena_pipeline.state.module_registry import (
    parse_requirements,
    requirement_strings,
    requirement_to_string,
)
from careena_pipeline.models import (
    AssessmentReadiness,
    DialogueState,
    MedicalCase,
    MessageUpdate,
    RecommendationGateDecision,
)


class DialogueStateManager:
    """
    Keeps dialogue/process state separate from the medical case while mirroring
    the legacy case fields for compatibility with the current UI and adapters.
    """

    def ensure_state(
        self,
        dialogue_state: DialogueState | None,
        case: MedicalCase | None = None,
    ) -> DialogueState:
        state = dialogue_state or DialogueState()
        if case is not None:
            state.active_case_id = case.case_id
            case.ensure_primary_problem()
            if state.focus_observation_id is None:
                state.focus_observation_id = case.primary_problem_id
            if state.focus_label is None:
                state.focus_label = case.primary_focus_label()
        return state

    def apply_message_update(
        self,
        state: DialogueState,
        message_update: MessageUpdate,
        case: MedicalCase | None = None,
    ) -> DialogueState:
        state.recommendation_requested = message_update.user_requests_recommendation
        state.recommended_modules = list(message_update.recommended_modules)
        if message_update.active_modules:
            state.active_modules = list(message_update.active_modules)

        if message_update.possible_new_topic:
            state.current_topic_status = "possible_topic_shift"
        elif state.current_topic_status != "ambiguous":
            state.current_topic_status = "single_topic"

        if message_update.required_fields:
            existing = list(state.open_requirements)
            merged = parse_requirements(existing + list(message_update.required_fields))
            state.open_requirements = merged

        if message_update.resolved_fields:
            resolved = {
                key
                for key in requirement_strings(message_update.resolved_fields)
            }
            state.resolved_requirements = parse_requirements(
                list(state.resolved_requirements) + list(message_update.resolved_fields)
            )
            state.open_requirements = [
                item
                for item in state.open_requirements
                if requirement_to_string(item) not in resolved
            ]
            if requirement_to_string(state.pending_followup) in resolved:
                state.pending_followup = None

        if case is not None:
            case.ensure_primary_problem()
            state.active_case_id = case.case_id
            state.focus_observation_id = case.primary_problem_id
            state.focus_label = case.primary_focus_label()

        return state

    def apply_readiness(
        self,
        state: DialogueState,
        readiness: AssessmentReadiness,
        case: MedicalCase | None = None,
    ) -> DialogueState:
        requirements = parse_requirements(
            readiness.blocking_requirements or readiness.missing_information
        )
        state.open_requirements = requirements
        if requirements:
            state.resolved_requirements = [
                item
                for item in state.resolved_requirements
                if requirement_to_string(item) not in {
                    requirement_to_string(requirement)
                    for requirement in requirements
                }
            ]
        if readiness.disambiguation_needed:
            state.current_topic_status = "ambiguous"
        elif state.current_topic_status != "possible_topic_shift":
            state.current_topic_status = "single_topic"
        if readiness.recommended_modules:
            state.recommended_modules = list(readiness.recommended_modules)

        if case is not None:
            case.ensure_primary_problem()
            state.focus_observation_id = case.primary_problem_id
            state.focus_label = case.primary_focus_label()

        return state

    def apply_planning_outcome(
        self,
        state: DialogueState,
        *,
        readiness: AssessmentReadiness,
        gate: RecommendationGateDecision,
        case: MedicalCase | None = None,
    ) -> DialogueState:
        self.apply_readiness(state, readiness, case)
        self.apply_gate(state, gate)
        if case is not None:
            case.ensure_primary_problem()
            state.focus_observation_id = case.primary_problem_id
            state.focus_label = case.primary_focus_label()
        return state

    def apply_gate(
        self,
        state: DialogueState,
        gate: RecommendationGateDecision,
    ) -> DialogueState:
        if gate.action == "ask_followup":
            if gate.missing_information:
                pending = parse_requirements([gate.missing_information[0]])
                state.pending_followup = pending[0] if pending else None
                state.last_question_key = (
                    requirement_to_string(state.pending_followup)
                    if state.pending_followup is not None
                    else None
                )
            state.awaiting_confirmation = False
        elif gate.action == "confirm_information":
            state.awaiting_confirmation = True
            state.pending_followup = None
            state.last_question_key = None
        else:
            state.awaiting_confirmation = False
            state.pending_followup = None
            state.last_question_key = None

        if gate.activated_modules:
            state.recommended_modules = list(gate.activated_modules)

        return state

    def sync_case(
        self,
        case: MedicalCase | None,
        state: DialogueState,
    ) -> MedicalCase | None:
        if case is None:
            return None

        if state.focus_observation_id is not None:
            case.primary_problem_id = state.focus_observation_id
        else:
            case.ensure_primary_problem()
        return case
