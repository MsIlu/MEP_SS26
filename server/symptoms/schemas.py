from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


SymptomSource = Literal["manual", "careena"]


class SymptomCreateRequest(BaseModel):
    """
    Request body for creating one symptom diary entry.
    """

    date: datetime
    symptom: str = Field(min_length=1, max_length=255)
    body_area: str = Field(default="", alias="bodyArea", max_length=100)
    intensity: int = Field(ge=1, le=10)
    temperature_c: float | None = Field(
        default=None, alias="temperatureC", ge=30, le=45
    )
    note: str = ""
    source: SymptomSource = "manual"
    created_at: datetime | None = Field(default=None, alias="createdAt")

    class Config:
        populate_by_name = True


class SymptomUpdateRequest(BaseModel):
    """Request body for patching an existing symptom diary entry."""

    date: datetime | None = None
    symptom: str | None = Field(default=None, min_length=1, max_length=255)
    body_area: str | None = Field(default=None, alias="bodyArea", max_length=100)
    intensity: int | None = Field(default=None, ge=1, le=10)
    temperature_c: float | None = Field(
        default=None, alias="temperatureC", ge=30, le=45
    )
    note: str | None = None

    class Config:
        populate_by_name = True


class SymptomDeleteResponse(BaseModel):
    """
    Response body returned after a symptom entry has been deleted.
    """

    message: str


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
    temperature_c: float | None = Field(alias="temperatureC")
    note: str
    source: SymptomSource
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True
