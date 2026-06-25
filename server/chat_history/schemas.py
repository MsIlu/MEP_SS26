from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

# Chat history differs between active and completed chats.
ChatHistoryStatus = Literal["active", "completed"]


class ChatHistoryMessage(BaseModel):
    text: str
    is_user: bool
    timestamp: Optional[datetime] = None
    can_export_pdf: bool = False
    export_title: Optional[str] = None
    export_recommendation: Optional[str] = None
    export_next_steps: Optional[str] = None


class ChatHistoryCreateRequest(BaseModel):
    profile_id: int
    session_id: Optional[str] = None
    title: Optional[str] = None
    status: ChatHistoryStatus = "completed"
    is_emergency: bool = False
    recommendation: str = ""
    next_steps: Optional[str] = None
    messages: list[ChatHistoryMessage]


class ChatHistoryUpdateRequest(BaseModel):
    session_id: Optional[str] = None
    title: Optional[str] = None
    status: ChatHistoryStatus = "active"
    is_emergency: bool = False
    recommendation: str = ""
    next_steps: Optional[str] = None
    messages: list[ChatHistoryMessage]


class ChatHistoryResponse(BaseModel):
    id: int
    profile_id: int
    session_id: Optional[str] = None
    title: Optional[str] = None
    status: ChatHistoryStatus = "completed"
    is_emergency: bool = False
    created_at: datetime
    updated_at: datetime
    recommendation: str = ""
    next_steps: Optional[str] = None
    messages: list[ChatHistoryMessage]


class ChatHistoryResumeResponse(BaseModel):
    session_id: str
    restored: bool
