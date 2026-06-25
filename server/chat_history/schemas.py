from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

# Chat history differs between active, waiting, completed and failed chats.
ChatHistoryStatus = Literal[
    "active",
    "waiting_for_assistant",
    "completed",
    "failed",
]


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


class ChatHistoryContinueResponse(BaseModel):
    session_id: str
    response: str
    red_flag: bool = False
    severity: Optional[str] = None
    action: Optional[str] = None
    rule_id: Optional[str] = None
    rule_name: Optional[str] = None
    category: Optional[str] = None
    message_key: Optional[str] = None
    matched_keywords: list[str] = []
    response_mode: Optional[str] = None
    recommendation_ready: bool = False
    recommendation_result: Optional[dict] = None
