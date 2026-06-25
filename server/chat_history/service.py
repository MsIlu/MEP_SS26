from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlmodel import Session, select

from careena4.models.turn import TurnInput
from database.models import ChatHistory, User
from profiles.service import get_profile_access_role
from chat_history.schemas import (
    ChatHistoryContinueResponse,
    ChatHistoryCreateRequest,
    ChatHistoryResponse,
    ChatHistoryResumeResponse,
    ChatHistoryUpdateRequest,
)


def list_chat_history(
        profile_id: int,
        current_user: User,
        session: Session,
) -> list[ChatHistoryResponse]:
    get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=session,
    )

    entries = session.exec(
        select(ChatHistory)
        .where(ChatHistory.profile_id == profile_id)
        .order_by(ChatHistory.created_at.desc())
    ).all()

    return [_to_response(entry) for entry in entries]


def create_chat_history(
        request: ChatHistoryCreateRequest,
        current_user: User,
        session: Session,
) -> ChatHistoryResponse:
    get_profile_access_role(
        account_id=current_user.id,
        profile_id=request.profile_id,
        session=session,
    )

    entry = ChatHistory(
        profile_id=request.profile_id,
        session_id=request.session_id,
        title=request.title,
        status=request.status,
        is_emergency=request.is_emergency,
        recommendation=request.recommendation,
        next_steps=request.next_steps,
        messages=[message.model_dump(mode="json") for message in request.messages],
    )

    session.add(entry)
    session.commit()
    session.refresh(entry)

    return _to_response(entry)


def update_chat_history(
        history_id: int,
        request: ChatHistoryUpdateRequest,
        current_user: User,
        session: Session,
) -> ChatHistoryResponse:
    entry = session.get(ChatHistory, history_id)

    if entry is None:
        raise HTTPException(status_code=404, detail="Chat history entry not found.")

    get_profile_access_role(
        account_id=current_user.id,
        profile_id=entry.profile_id,
        session=session,
    )

    entry.session_id = request.session_id
    entry.title = request.title
    entry.status = request.status
    entry.is_emergency = request.is_emergency
    entry.recommendation = request.recommendation
    entry.next_steps = request.next_steps
    entry.messages = [message.model_dump(mode="json") for message in request.messages]
    entry.updated_at = datetime.utcnow()

    session.add(entry)
    session.commit()
    session.refresh(entry)

    return _to_response(entry)


def resume_chat_history(
        history_id: int,
        current_user: User,
        session: Session,
        session_store,
        session_profiles: dict[str, int | None],
) -> ChatHistoryResumeResponse:
    entry = session.get(ChatHistory, history_id)

    if entry is None:
        raise HTTPException(status_code=404, detail="Chat history entry not found.")

    get_profile_access_role(
        account_id=current_user.id,
        profile_id=entry.profile_id,
        session=session,
    )

    if entry.status not in {"active", "waiting_for_assistant"}:
        raise HTTPException(
            status_code=409,
            detail="Only active chat history entries can be resumed.",
        )

    if entry.session_id is not None and session_store.get(entry.session_id) is not None:
        return ChatHistoryResumeResponse(
            session_id=entry.session_id,
            restored=False,
        )

    session_id = session_store.create_session()
    restored_session = session_store.get(session_id)

    if restored_session is not None:
        restored_session.messages = _history_messages_to_careena4_messages(
            entry.messages
        )

    session_profiles[session_id] = entry.profile_id
    entry.session_id = session_id
    entry.updated_at = datetime.utcnow()

    session.add(entry)
    session.commit()

    return ChatHistoryResumeResponse(
        session_id=session_id,
        restored=True,
    )


def continue_chat_history(
        history_id: int,
        current_user: User,
        session: Session,
        session_store,
        session_profiles: dict[str, int | None],
        turn_engine,
        response_builder,
) -> ChatHistoryContinueResponse:
    entry = session.get(ChatHistory, history_id)

    if entry is None:
        raise HTTPException(status_code=404, detail="Chat history entry not found.")

    get_profile_access_role(
        account_id=current_user.id,
        profile_id=entry.profile_id,
        session=session,
    )

    if entry.status != "waiting_for_assistant":
        raise HTTPException(
            status_code=409,
            detail="Only waiting chat history entries can be continued.",
        )

    last_user_message = _last_message(entry.messages)

    if last_user_message is None or last_user_message.get("is_user") is not True:
        raise HTTPException(
            status_code=409,
            detail="Chat history does not wait for an assistant response.",
        )

    user_text = str(last_user_message.get("text", "")).strip()

    if not user_text:
        raise HTTPException(
            status_code=409,
            detail="Last user message is empty.",
        )

    if entry.session_id is not None and session_store.get(entry.session_id) is not None:
        session_id = entry.session_id
    else:
        session_id = session_store.create_session()
        entry.session_id = session_id

    careena4_session = session_store.get(session_id)

    if careena4_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    previous_messages = entry.messages[:-1]
    careena4_session.messages = _history_messages_to_careena4_messages(
        previous_messages
    )
    session_profiles[session_id] = entry.profile_id

    try:
        turn_result = turn_engine.run_turn(
            TurnInput.from_persisted_state(
                message=user_text,
                session_id=session_id,
                turn_id=str(uuid4()),
                conversation_messages=careena4_session.messages,
                persisted_case_topic=careena4_session.case_topic,
                persisted_medical_case=careena4_session.medical_case,
                persisted_conversation_state=careena4_session.conversation_state,
                persisted_recommendation_state=careena4_session.recommendation_state,
                persisted_symptom_input_draft=careena4_session.symptom_input_draft,
            )
        )
    except Exception as exc:
        entry.status = "failed"
        entry.updated_at = datetime.utcnow()
        session.add(entry)
        session.commit()
        raise HTTPException(
            status_code=500,
            detail="Assistant response could not be continued.",
        ) from exc

    careena4_session.case_topic = turn_result.case_topic
    careena4_session.medical_case = turn_result.medical_case
    careena4_session.conversation_state = turn_result.conversation_state
    careena4_session.recommendation_state = turn_result.recommendation_state
    careena4_session.last_turn_understanding = turn_result.current_turn_understanding

    if turn_result.symptom_input_draft is not None:
        careena4_session.symptom_input_draft = turn_result.symptom_input_draft

    careena4_session.messages.append({"role": "user", "content": user_text})

    response = response_builder(turn_result)
    assistant_text = str(response.get("response", ""))

    careena4_session.messages.append(
        {"role": "assistant", "content": assistant_text}
    )

    recommendation_result = response.get("recommendation_result")
    recommendation_allowed = (
        isinstance(recommendation_result, dict)
        and recommendation_result.get("allowed") is True
    )
    is_completed = response.get("red_flag") is True or (
        response.get("response_mode") == "recommend" and recommendation_allowed
    )

    entry.messages = [
        *entry.messages,
        {
            "text": assistant_text,
            "is_user": False,
            "can_export_pdf": is_completed,
            "export_title": "Handlungsempfehlung" if is_completed else None,
            "export_recommendation": (
                recommendation_result.get("summary")
                if isinstance(recommendation_result, dict)
                else assistant_text
            ),
            "export_next_steps": response.get("action"),
        },
    ]

    if is_completed:
        entry.status = "completed"
        entry.is_emergency = response.get("red_flag") is True
        entry.recommendation = (
            recommendation_result.get("summary")
            if isinstance(recommendation_result, dict)
            else assistant_text
        )
        entry.next_steps = response.get("action")
    else:
        entry.status = "active"

    entry.updated_at = datetime.utcnow()

    session.add(entry)
    session.commit()

    return ChatHistoryContinueResponse(
        session_id=session_id,
        **response,
    )


def _to_response(entry: ChatHistory) -> ChatHistoryResponse:
    return ChatHistoryResponse(
        id=entry.id,
        profile_id=entry.profile_id,
        session_id=entry.session_id,
        title=entry.title,
        status=entry.status,
        is_emergency=entry.is_emergency,
        created_at=_as_utc(entry.created_at),
        updated_at=_as_utc(entry.updated_at),
        recommendation=entry.recommendation,
        next_steps=entry.next_steps,
        messages=entry.messages,
    )


def _last_message(messages: list[dict]) -> dict | None:
    if not messages:
        return None

    return messages[-1]


def _history_messages_to_careena4_messages(messages: list[dict]) -> list[dict[str, str]]:
    restored_messages: list[dict[str, str]] = []

    for message in messages:
        text = str(message.get("text", "")).strip()
        if not text:
            continue

        role = "user" if message.get("is_user") is True else "assistant"
        restored_messages.append({"role": role, "content": text})

    return restored_messages


def _as_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)
