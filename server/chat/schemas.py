"""Request models for the Careena4 chat endpoints."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str
    profile_id: int | None = None


class SessionRequest(BaseModel):
    profile_id: int | None = None


class RecommendationRequest(BaseModel):
    session_id: str


class SetObservationSeveritiesRequest(BaseModel):
    session_id: str
    severities: dict[str, int]  # symptom label -> severity (1-10)
