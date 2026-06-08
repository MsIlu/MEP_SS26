"""
Shared context builders for Careena's message-level LLM calls.

Phase 2 keeps Call 1 and Call 2 on the same technical context shape for now,
but exposes separate builder entrypoints so their contracts stay readable and
can diverge later without another broad rename.
"""

from careena_pipeline.planning.requirement_state import requirement_key, requirement_keys
from careena_pipeline.models import (
    CaseSummary,
    CaseSummaryObservation,
    CaseUpdateContext,
    ConversationTurn,
    DialogueState,
    DialogueSummary,
    IntentGateway,
    MedicalCase,
    StagedFollowupAnswer,
)


MAX_RECENT_TURNS = 4


def build_intent_gateway_context(
    *,
    latest_user_message: str,
    existing_case: MedicalCase | None = None,
    dialogue_state: DialogueState | None = None,
    pending_slot: str | None = None,
    messages: list[dict[str, str]] | None = None,
) -> CaseUpdateContext:
    return _build_shared_message_context(
        latest_user_message=latest_user_message,
        existing_case=existing_case,
        dialogue_state=dialogue_state,
        pending_slot=pending_slot,
        intent_gateway=None,
        messages=messages,
    )


def build_case_update_context(
    *,
    latest_user_message: str,
    existing_case: MedicalCase | None = None,
    dialogue_state: DialogueState | None = None,
    pending_slot: str | None = None,
    intent_gateway: IntentGateway | None = None,
    staged_followup_answers: list[StagedFollowupAnswer] | None = None,
    messages: list[dict[str, str]] | None = None,
) -> CaseUpdateContext:
    return _build_shared_message_context(
        latest_user_message=latest_user_message,
        existing_case=existing_case,
        dialogue_state=dialogue_state,
        pending_slot=pending_slot,
        intent_gateway=intent_gateway,
        staged_followup_answers=staged_followup_answers,
        messages=messages,
    )


def _build_shared_message_context(
    *,
    latest_user_message: str,
    existing_case: MedicalCase | None = None,
    dialogue_state: DialogueState | None = None,
    pending_slot: str | None = None,
    intent_gateway: IntentGateway | None = None,
    staged_followup_answers: list[StagedFollowupAnswer] | None = None,
    messages: list[dict[str, str]] | None = None,
) -> CaseUpdateContext:
    recent_turns = _recent_turns(messages, latest_user_message=latest_user_message)
    last_assistant_question = _last_assistant_question(recent_turns)

    return CaseUpdateContext(
        latest_user_message=latest_user_message,
        pending_slot=pending_slot,
        last_assistant_question=last_assistant_question,
        recent_turns=recent_turns,
        intent_gateway=intent_gateway,
        case_summary=_summarize_case(existing_case, dialogue_state),
        dialogue_summary=_summarize_dialogue(
            dialogue_state,
            existing_case,
            staged_followup_answers=staged_followup_answers,
        ),
    )


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


def _summarize_case(
    existing_case: MedicalCase | None,
    dialogue_state: DialogueState | None,
) -> CaseSummary | None:
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


def _summarize_dialogue(
    dialogue_state: DialogueState | None,
    existing_case: MedicalCase | None,
    *,
    staged_followup_answers: list[StagedFollowupAnswer] | None = None,
) -> DialogueSummary | None:
    if dialogue_state is None and existing_case is None:
        return None

    return DialogueSummary(
        current_topic_status=(
            dialogue_state.current_topic_status
            if dialogue_state is not None
            else "single_topic"
        ),
        last_question_key=(
            dialogue_state.last_question_key
            if dialogue_state is not None
            else None
        ),
        active_modules=(
            list(dialogue_state.active_modules)
            if dialogue_state is not None
            else []
        ),
        open_requirements=(
            requirement_keys(dialogue_state.open_requirements)
            if dialogue_state is not None
            else []
        ),
        pending_followup=(
            requirement_key(dialogue_state.pending_followup)
            if dialogue_state is not None
            else None
        ),
        staged_followup_answers=(
            list(staged_followup_answers)
            if staged_followup_answers is not None
            else (
                list(dialogue_state.staged_followup_answers)
                if dialogue_state is not None
                else []
            )
        ),
        awaiting_confirmation=(
            dialogue_state.awaiting_confirmation
            if dialogue_state is not None
            else False
        ),
        recommendation_requested=(
            dialogue_state.recommendation_requested
            if dialogue_state is not None
            else False
        ),
        recommended_modules=(
            list(dialogue_state.recommended_modules)
            if dialogue_state is not None
            else []
        ),
    )
