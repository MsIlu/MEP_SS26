from careena_pipeline3.models.common import Call2OperationMode, Call2Task
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.extraction import ExtractionResult
from careena_pipeline3.models.workflow import (
    CaseSummary,
    CaseSummaryObservation,
    ConversationTurn,
    DialogueSummary,
    IntentGatewayContext,
)


MAX_RECENT_TURNS = 4


def build_intent_gateway_context(
    *,
    latest_user_message: str,
    existing_case: MedicalCase | None = None,
    dialogue_state: DialogueState | None = None,
    pending_slot: str | None = None,
    messages: list[dict[str, str]] | None = None,
) -> IntentGatewayContext:
    recent_turns = _recent_turns(messages, latest_user_message=latest_user_message)
    last_assistant_question = _last_assistant_question(recent_turns)

    return IntentGatewayContext(
        latest_user_message=latest_user_message,
        pending_slot=pending_slot,
        last_assistant_question=last_assistant_question,
        recent_turns=recent_turns,
        intent_gateway=None,
        case_summary=None,
        dialogue_summary=None,
    )


def build_case_extraction_input(
    *,
    latest_user_message: str,
    existing_case: MedicalCase | None = None,
    dialogue_state: DialogueState | None = None,
    pending_slot: str | None = None,
    call2_tasks: list[Call2Task] | None = None,
    operation_mode: Call2OperationMode | None = None,
    messages: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    """
    Builds the constrained Call-2 payload.

    Important policy:
    - `latest_user_message` stays the primary fact source.
    - focus/pending/dialogue/case fields are only interpretive control
      signals.
    - these context fields must not become an independent source for newly
      materialized medical facts.
    """
    focus_observation = (
        existing_case.primary_observation() if existing_case is not None else None
    )
    return {
        "latest_user_message": latest_user_message,
        "call2_tasks": list(call2_tasks or []),
        "operation_mode": operation_mode,
        "target_scope": _target_scope_for_mode(operation_mode),
        "allow_new_observations": _allow_new_observations_for_mode(operation_mode),
        "pending_slot": pending_slot,
        "focus_observation_id": (
            focus_observation.id if focus_observation is not None else None
        ),
        "focus_label": (
            focus_observation.patient_label if focus_observation is not None else None
        ),
        "focus_type": (
            focus_observation.type if focus_observation is not None else None
        ),
        "last_assistant_question": _last_assistant_question(
            _recent_turns(messages, latest_user_message=latest_user_message)
        ),
        "case_summary": (
            _summarize_case(existing_case).model_dump() if existing_case is not None else None
        ),
        "dialogue_summary": (
            _summarize_dialogue(dialogue_state).model_dump()
            if dialogue_state is not None
            else None
        ),
    }


def build_extraction_normalization_input(
    *,
    latest_user_message: str,
    extraction_result: ExtractionResult,
    existing_case: MedicalCase | None = None,
    dialogue_state: DialogueState | None = None,
    pending_slot: str | None = None,
    call2_tasks: list[Call2Task] | None = None,
    operation_mode: Call2OperationMode | None = None,
    messages: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    focus_observation = (
        existing_case.primary_observation() if existing_case is not None else None
    )
    return {
        "latest_user_message": latest_user_message,
        "operation_mode": operation_mode,
        "target_scope": _target_scope_for_mode(operation_mode),
        "allow_new_observations": _allow_new_observations_for_mode(operation_mode),
        "call2_tasks": list(call2_tasks or []),
        "pending_slot": pending_slot,
        "focus_observation_id": (
            focus_observation.id if focus_observation is not None else None
        ),
        "focus_label": (
            focus_observation.patient_label if focus_observation is not None else None
        ),
        "focus_type": (
            focus_observation.type if focus_observation is not None else None
        ),
        "last_assistant_question": _last_assistant_question(
            _recent_turns(messages, latest_user_message=latest_user_message)
        ),
        "case_summary": (
            _summarize_case(existing_case).model_dump() if existing_case is not None else None
        ),
        "dialogue_summary": (
            _summarize_dialogue(dialogue_state).model_dump()
            if dialogue_state is not None
            else None
        ),
        "initial_extraction_result": extraction_result.model_dump(),
    }


def _target_scope_for_mode(
    operation_mode: Call2OperationMode | None,
) -> str:
    if operation_mode == "followup_slot_update":
        return "focus_only"
    if operation_mode == "existing_fact_revision":
        return "existing_focus_revision"
    if operation_mode == "mixed_update_and_new_info":
        return "focus_plus_new"
    if operation_mode == "no_medical_update_expected":
        return "none"
    return "free"


def _allow_new_observations_for_mode(
    operation_mode: Call2OperationMode | None,
) -> bool:
    return operation_mode in {
        None,
        "focused_new_fact_extraction",
        "mixed_update_and_new_info",
    }


def _recent_turns(
    messages: list[dict[str, str]] | None,
    *,
    latest_user_message: str,
) -> list[ConversationTurn]:
    if not messages:
        return []

    normalized_messages = [
        turn
        for turn in (_normalize_turn(message) for message in messages)
        if turn is not None
    ]
    if not normalized_messages:
        return []

    if (
        normalized_messages[-1].role == "user"
        and normalized_messages[-1].content.strip() == latest_user_message.strip()
    ):
        normalized_messages = normalized_messages[:-1]

    return normalized_messages[-MAX_RECENT_TURNS:]


def _normalize_turn(message: dict[str, str] | None) -> ConversationTurn | None:
    if not message:
        return None

    role = (message.get("role") or "").strip().lower()
    content = (message.get("content") or "").strip()
    if not role or not content:
        return None

    role_aliases = {
        "patient": "user",
        "careena": "assistant",
    }
    normalized_role = role_aliases.get(role, role)
    if normalized_role not in {"user", "assistant", "system"}:
        return None

    return ConversationTurn(role=normalized_role, content=content)


def _last_assistant_question(recent_turns: list[ConversationTurn]) -> str | None:
    for turn in reversed(recent_turns):
        if turn.role == "assistant":
            return turn.content
    return None


def _summarize_case(existing_case: MedicalCase | None) -> CaseSummary | None:
    if existing_case is None:
        return None

    existing_case.ensure_primary_problem()
    observations = [
        CaseSummaryObservation(
            type=observation.type,
            display_label=observation.patient_label,
            concept=observation.concept,
            body_site=observation.runtime_value("body_site"),
            temporality=observation.runtime_value("temporality"),
            severity=observation.runtime_value("severity"),
            details=observation.details,
            status=observation.status,
        )
        for observation in existing_case.observations
        if observation.status != "user_rejected"
    ]

    return CaseSummary(
        subject_relation=existing_case.subject.relation,
        subject_age=existing_case.subject.age,
        primary_focus=existing_case.primary_focus_label(),
        primary_problem_id=existing_case.primary_problem_id,
        active_problem_ids=existing_case.active_problem_ids(),
        observations=observations[:6],
    )


def _summarize_dialogue(dialogue_state: DialogueState | None) -> DialogueSummary | None:
    if dialogue_state is None:
        return None

    return DialogueSummary(
        current_topic_status=dialogue_state.current_topic_status,
        active_modules=list(dialogue_state.active_modules),
        open_requirements=list(dialogue_state.open_requirements),
        pending_followup=dialogue_state.pending_followup,
        recommendation_requested=dialogue_state.recommendation_requested,
        recommended_modules=list(dialogue_state.recommended_modules),
    )
