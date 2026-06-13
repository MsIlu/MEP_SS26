from datetime import datetime

from pydantic import BaseModel, Field


class SymptomCreateRequest(BaseModel):
    """
    Request body for creating one symptom diary entry.
    """

    date: datetime
    symptom: str = Field(min_length=1, max_length=255)
    body_area: str = Field(default="", alias="bodyArea", max_length=100)
    intensity: int = Field(ge=1, le=10)
    note: str = ""
    created_at: datetime | None = Field(default=None, alias="createdAt")

    class Config:
        populate_by_name = True


class SymptomResponse(BaseModel):
    """
    Symptom diary entry returned to the frontend.
    """

    id: int
    profile_id: int
    date: datetime
    symptom: str
    body_area: str = Field(alias="bodyArea")
    intensity: int
    note: str
    created_at: datetime = Field(alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True
