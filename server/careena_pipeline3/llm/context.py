from careena_pipeline3.models.common import Call2OperationMode, Call2Task
from careena_pipeline3.models.domain import (
    DialogueState,
    MedicalCase,
    PendingChoicePrompt,
)
from careena_pipeline3.models.workflow import (
    ConversationTurn,
    IntentGatewayContext,
)


MAX_RECENT_TURNS = 4


def build_intent_gateway_context(
    *,
    latest_user_message: str,
    existing_case: MedicalCase | None = None,
    dialogue_state: DialogueState | None = None,
    pending_slot: str | None = None,
    history_messages: list[dict[str, str]] | None = None,
) -> IntentGatewayContext:
    recent_turns = _recent_turns(
        history_messages,
        latest_user_message=latest_user_message,
    )
    last_assistant_question = _last_assistant_question(recent_turns)
    pending_choice_prompt = (
        dialogue_state.pending_choice_prompt if dialogue_state is not None else None
    )

    return IntentGatewayContext(
        latest_user_message=latest_user_message,
        pending_slot=pending_slot,
        active_choice_prompt_kind=(
            pending_choice_prompt.kind
            if pending_choice_prompt is not None
            else None
        ),
        active_choice_prompt_code=(
            pending_choice_prompt.prompt_code
            if pending_choice_prompt is not None
            else None
        ),
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
    profile: str | None = None,
    call2_tasks: list[Call2Task] | None = None,
    operation_mode: Call2OperationMode | None = None,
    history_messages: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    """
    Builds the reduced primary Call-2 payload.

    Important policy:
    - `latest_user_message` stays the primary fact source.
    - surrounding fields are only small interpretive control signals.
    - these context fields must not become an independent source for newly
      materialized medical facts.
    - this payload is intentionally the small base structure; later Block-4/8
      work may assemble it more dynamically from Call-1 dispatch signals, but
      broad case/dialogue summaries should not re-enter by default.
    """
    recent_turns = _recent_turns(
        history_messages,
        latest_user_message=latest_user_message,
    )
    return {
        "latest_user_message": latest_user_message,
        "profile": profile or "default",
        "call2_tasks": list(call2_tasks or []),
        "operation_mode": operation_mode,
        "pending_slot": pending_slot,
        "last_assistant_question": _last_assistant_question(recent_turns),
        "focus_observation": _focus_observation_for_call2(
            existing_case=existing_case,
            operation_mode=operation_mode,
            pending_slot=pending_slot,
        ),
        "relevant_existing_observations": _relevant_existing_observations_for_call2(
            existing_case=existing_case,
            operation_mode=operation_mode,
        ),
    }


def build_recommendation_transition_input(
    *,
    latest_user_message: str,
    pending_choice_prompt: PendingChoicePrompt,
    history_messages: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    recent_turns = _recent_turns(
        history_messages,
        latest_user_message=latest_user_message,
    )
    return {
        "latest_user_message": latest_user_message,
        "prompt_kind": pending_choice_prompt.kind,
        "prompt_code": pending_choice_prompt.prompt_code,
        "allowed_actions": list(pending_choice_prompt.allowed_actions),
        "last_assistant_question": _last_assistant_question(recent_turns),
        "recent_turns": [turn.model_dump() for turn in recent_turns],
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


def _focus_observation_for_call2(
    *,
    existing_case: MedicalCase | None,
    operation_mode: Call2OperationMode | None,
    pending_slot: str | None,
) -> dict[str, object] | None:
    if existing_case is None:
        return None

    if pending_slot is not None or operation_mode in {
        "followup_slot_update",
        "mixed_update_and_new_info",
    }:
        # Legacy requirement followup path; active requirement followups no
        # longer derive Call-2 focus from pending slots or followup modes.
        return None

    needs_focus = operation_mode in {"existing_fact_revision"}
    if not needs_focus:
        return None

    focus = existing_case.primary_observation()
    if focus is None:
        return None

    attributes: dict[str, object] = {}
    for key in (
        "body_site",
        "temporality",
        "severity",
        "injury_context",
        "functional_limitation",
    ):
        value = focus.runtime_value(key)
        if value not in (None, "", []):
            attributes[key] = value

    return {
        "type": focus.type,
        "label": focus.patient_label,
        "concept": focus.concept,
        "attributes": attributes,
    }


def _relevant_existing_observations_for_call2(
    *,
    existing_case: MedicalCase | None,
    operation_mode: Call2OperationMode | None,
) -> list[dict[str, object]] | None:
    if existing_case is None:
        return None
    if operation_mode not in {"existing_fact_revision"}:
        return None

    observations = []
    for observation in existing_case.observations[:3]:
        if observation.status == "user_rejected":
            continue
        attributes: dict[str, object] = {}
        for key in ("body_site", "temporality", "severity"):
            value = observation.runtime_value(key)
            if value not in (None, "", []):
                attributes[key] = value
        observations.append(
            {
                "type": observation.type,
                "label": observation.patient_label,
                "concept": observation.concept,
                "attributes": attributes,
            }
        )
    return observations or None
