from datetime import timezone

from sqlmodel import Session, select

from database.models import ChatHistory, User
from profiles.service import get_profile_access_role
from chat_history.schemas import ChatHistoryCreateRequest, ChatHistoryResponse


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


def _to_response(entry: ChatHistory) -> ChatHistoryResponse:
    return ChatHistoryResponse(
        id=entry.id,
        profile_id=entry.profile_id,
        title=entry.title,
        status=entry.status,
        is_emergency=entry.is_emergency,
        created_at=_as_utc(entry.created_at),
        updated_at=_as_utc(entry.updated_at),
        recommendation=entry.recommendation,
        next_steps=entry.next_steps,
        messages=entry.messages,
    )


def _as_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)
