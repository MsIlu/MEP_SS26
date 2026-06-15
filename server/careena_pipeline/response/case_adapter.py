from careena_pipeline.planning.requirement_state import requirement_key, requirement_keys
from careena_pipeline.models import DialogueState, MedicalCase


def case_to_payload(
    case: MedicalCase,
    *,
    dialogue_state: DialogueState | None = None,
) -> dict:
    primary = case.primary_observation()
    return {
        "case_id": case.case_id,
        "subject": case.subject.model_dump(),
        "primary_problem_id": case.primary_problem_id,
        "primary_focus": case.primary_focus_label(),
        "active_problem_ids": case.active_problem_ids(),
        "observations": [observation.model_dump() for observation in case.observations],
        "dialogue": {
            "pending_followup": (
                requirement_key(dialogue_state.pending_followup)
                if dialogue_state
                else None
            ),
            "open_requirements": (
                requirement_keys(dialogue_state.open_requirements)
                if dialogue_state
                else []
            ),
            "focus_observation_id": (
                dialogue_state.focus_observation_id
                if dialogue_state
                else (primary.id if primary is not None else case.primary_problem_id)
            ),
            "focus_label": (
                dialogue_state.focus_label
                if dialogue_state
                else case.primary_focus_label()
            ),
        },
    }
