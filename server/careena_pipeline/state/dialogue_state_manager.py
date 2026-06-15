from careena_pipeline.planning.requirement_state import (
    build_requirement_state,
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
    StagedFollowupAnswer,
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
        intent_signals = message_update.intent_signals
        planner_hints = message_update.planner_hints
        requirement_hints = message_update.requirement_hints

        state.recommendation_requested = planner_hints.recommendation_requested
        state.recommended_modules = list(planner_hints.recommended_modules)
        if requirement_hints.active_modules:
            state.active_modules = list(requirement_hints.active_modules)
        self._apply_staged_followup_answers(state, message_update)

        if intent_signals.possible_new_topic:
            state.current_topic_status = "possible_topic_shift"
        elif state.current_topic_status != "ambiguous":
            state.current_topic_status = "single_topic"

        if requirement_hints.required_fields:
            state.open_requirements = merge_requirements(
                state.open_requirements,
                requirement_hints.required_fields,
            )

        return self.focus_sync.sync_state_from_case(state, case)

    @staticmethod
    def _apply_staged_followup_answers(
        state: DialogueState,
        message_update: MessageUpdate,
    ) -> None:
        staging_hints = message_update.staging_hints
        if staging_hints.clear_staged_followup_answers:
            state.staged_followup_answers = []

        if not staging_hints.staged_followup_answers:
            return

        staged_by_key: dict[tuple[str, str | None], StagedFollowupAnswer] = {
            (item.requirement_key, item.focus_observation_id): item
            for item in state.staged_followup_answers
        }
        for item in staging_hints.staged_followup_answers:
            staged_by_key[(item.requirement_key, item.focus_observation_id)] = item
        state.staged_followup_answers = list(staged_by_key.values())

    def sync_requirement_progress(
        self,
        state: DialogueState,
        *,
        case: MedicalCase,
        message_update: MessageUpdate | None = None,
    ) -> DialogueState:
        requirement_state = build_requirement_state(
            case=case,
            dialogue_state=state,
            message_update=message_update,
        )
        blocking_requirements = list(requirement_state.blocking_requirements)
        resolved_requirements = list(requirement_state.resolved_fields.values())

        state.active_modules = list(requirement_state.active_modules)
        state.open_requirements = blocking_requirements
        state.resolved_requirements = resolved_requirements

        pending_key = requirement_key(state.pending_followup)
        if pending_key not in set(requirement_keys(blocking_requirements)):
            state.pending_followup = None
            state.last_question_key = None

        return self.focus_sync.sync_state_from_case(state, case)

    def apply_readiness(
        self,
        state: DialogueState,
        readiness: AssessmentReadiness,
        case: MedicalCase | None = None,
    ) -> DialogueState:
        if case is not None:
            self.sync_requirement_progress(state, case=case)
            requirements = list(state.open_requirements)
        else:
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
            state.awaiting_confirmation = False
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
