from fastapi import HTTPException
from datetime import datetime, timezone

from sqlmodel import Session, select

from database.models import ChatHistory, User
from profiles.service import get_profile_access_role
from chat_history.schemas import (
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

    if entry.status != "active":
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
