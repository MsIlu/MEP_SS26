from careena_pipeline.planning.requirement_state import (
    first_requirement,
    merge_requirements,
    remove_requirements,
    requirement_key,
    requirement_keys,
)
from careena_pipeline.models import (
    AssessmentReadiness,
    DialogueState,
    MedicalCase,
    MessageUpdate,
    RecommendationGateDecision,
)
from careena_pipeline.state.dialogue_focus_sync import DialogueFocusSync


class DialogueStateManager:
    """
    Applies process-state mutations for the running dialogue.

    Focus and case-link synchronization are delegated to a dedicated
    compatibility bridge so this class can stay closer to actual process
    state transitions.
    """

    def __init__(
        self,
        *,
        focus_sync: DialogueFocusSync | None = None,
    ):
        self.focus_sync = focus_sync or DialogueFocusSync()

    def ensure_state(
        self,
        dialogue_state: DialogueState | None,
        case: MedicalCase | None = None,
    ) -> DialogueState:
        state = dialogue_state or DialogueState()
        return self.focus_sync.ensure_state_links(state, case)

    def apply_message_update(
        self,
        state: DialogueState,
        message_update: MessageUpdate,
        case: MedicalCase | None = None,
    ) -> DialogueState:
        planner_hints = message_update.planner_hints
        requirement_hints = message_update.requirement_hints

        state.recommendation_requested = planner_hints.recommendation_requested
        state.recommended_modules = list(planner_hints.recommended_modules)
        if requirement_hints.active_modules:
            state.active_modules = list(requirement_hints.active_modules)

        if message_update.possible_new_topic:
            state.current_topic_status = "possible_topic_shift"
        elif state.current_topic_status != "ambiguous":
            state.current_topic_status = "single_topic"

        if requirement_hints.required_fields:
            state.open_requirements = merge_requirements(
                state.open_requirements,
                requirement_hints.required_fields,
            )

        if requirement_hints.resolved_fields:
            state.resolved_requirements = merge_requirements(
                state.resolved_requirements,
                requirement_hints.resolved_fields,
            )
            state.open_requirements = remove_requirements(
                state.open_requirements,
                requirement_hints.resolved_fields,
            )
            if requirement_key(state.pending_followup) in set(
                requirement_keys(requirement_hints.resolved_fields)
            ):
                state.pending_followup = None
                state.last_question_key = None

        return self.focus_sync.sync_state_from_case(state, case)

    def apply_readiness(
        self,
        state: DialogueState,
        readiness: AssessmentReadiness,
        case: MedicalCase | None = None,
    ) -> DialogueState:
        requirements = merge_requirements(
            None,
            readiness.blocking_requirements or readiness.missing_information
        )
        state.open_requirements = requirements
        if requirements:
            state.resolved_requirements = remove_requirements(
                state.resolved_requirements,
                requirements,
            )
        if (
            state.pending_followup is not None
            and requirement_key(state.pending_followup) not in set(requirement_keys(requirements))
        ):
            state.pending_followup = None
            state.last_question_key = None
        if readiness.disambiguation_needed:
            state.current_topic_status = "ambiguous"
        elif state.current_topic_status != "possible_topic_shift":
            state.current_topic_status = "single_topic"

        return self.focus_sync.sync_state_from_case(state, case)

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
        return self.focus_sync.sync_state_from_case(state, case)

    def apply_gate(
        self,
        state: DialogueState,
        gate: RecommendationGateDecision,
    ) -> DialogueState:
        if gate.action == "ask_followup":
            if gate.missing_information:
                state.pending_followup = first_requirement(gate.missing_information)
                state.last_question_key = requirement_key(state.pending_followup)
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
        return self.focus_sync.sync_case_from_state(case, state)
