from careena_pipeline3.models.domain import DialogueState, MedicalCase


class DialogueFocusSync:
    """
    Keeps focus and case linkage in sync between DialogueState and MedicalCase.

    The service intentionally stays narrow. It synchronizes the observation
    cursor and case references, but does not own case-frame semantics,
    readiness, gating, or extraction policy.
    """

    def ensure_state_links(
        self,
        state: DialogueState,
        case: MedicalCase | None = None,
    ) -> DialogueState:
        if case is None:
            return state

        case.ensure_primary_problem()
        state.active_case_id = case.case_id
        if state.focus_observation_id is None:
            state.focus_observation_id = case.primary_problem_id
        if state.focus_label is None:
            state.focus_label = case.primary_focus_label()
        return state

    def sync_state_from_case(
        self,
        state: DialogueState,
        case: MedicalCase | None = None,
    ) -> DialogueState:
        if case is None:
            return state

        case.ensure_primary_problem()
        state.active_case_id = case.case_id
        state.focus_observation_id = case.primary_problem_id
        state.focus_label = case.primary_focus_label()
        return state

    def sync_case_from_state(
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
