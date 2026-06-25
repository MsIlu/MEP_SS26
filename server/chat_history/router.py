from fastapi import APIRouter, Depends
from sqlmodel import Session

from auth.security import get_current_account, get_session
from database.models import User
from chat_history.schemas import ChatHistoryCreateRequest, ChatHistoryResponse
from chat_history.service import create_chat_history, list_chat_history


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
