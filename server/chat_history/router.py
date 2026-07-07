"""HTTP routes for persisted chat history entries."""

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from auth.security import get_current_account, get_session
from database.models import User
from chat_history.schemas import (
    ChatHistoryContinueResponse,
    ChatHistoryCreateRequest,
    ChatHistoryResponse,
    ChatHistoryResumeResponse,
    ChatHistoryUpdateRequest,
)

from chat_history.service import (
    continue_chat_history,
    create_chat_history,
    delete_chat_history,
    list_chat_history,
    resume_chat_history,
    update_chat_history,
)

router = APIRouter(prefix="/chat-history", tags=["chat-history"])


@router.get("/{profile_id}", response_model=list[ChatHistoryResponse])
def get_chat_history(
        profile_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    return list_chat_history(
        profile_id=profile_id,
        current_user=current_user,
        session=session,
    )


@router.post("", response_model=ChatHistoryResponse)
def post_chat_history(
        request: ChatHistoryCreateRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    return create_chat_history(
        request=request,
        current_user=current_user,
        session=session,
    )


@router.patch("/{history_id}", response_model=ChatHistoryResponse)
def patch_chat_history(
        history_id: int,
        request: ChatHistoryUpdateRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    return update_chat_history(
        history_id=history_id,
        request=request,
        current_user=current_user,
        session=session,
    )


@router.post("/{history_id}/resume", response_model=ChatHistoryResumeResponse)
def post_resume_chat_history(
        history_id: int,
        request: Request,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    return resume_chat_history(
        history_id=history_id,
        current_user=current_user,
        session=session,
        session_store=request.app.state.careena4_session_store,
        session_profiles=request.app.state.careena4_session_profiles,
    )


@router.post("/{history_id}/continue", response_model=ChatHistoryContinueResponse)
def post_continue_chat_history(
        history_id: int,
        request: Request,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    return continue_chat_history(
        history_id=history_id,
        current_user=current_user,
        session=session,
        session_store=request.app.state.careena4_session_store,
        session_profiles=request.app.state.careena4_session_profiles,
        turn_engine=request.app.state.careena4_turn_engine,
        response_builder=request.app.state.careena4_response_builder,
    )


@router.delete("/{history_id}")
def delete_chat_history_entry(
        history_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    delete_chat_history(
        history_id=history_id,
        current_user=current_user,
        session=session,
    )
    return {"deleted": True}
