from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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
    title: Optional[str] = None
    is_emergency: bool = False
    recommendation: str
    next_steps: Optional[str] = None
    messages: list[ChatHistoryMessage]


class ChatHistoryResponse(BaseModel):
    id: int
    profile_id: int
    title: Optional[str] = None
    is_emergency: bool = False
    created_at: datetime
    recommendation: str
    next_steps: Optional[str] = None
    messages: list[ChatHistoryMessage]
