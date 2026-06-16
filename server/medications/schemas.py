# Request and response schemas for profile-scoped medication entries.

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


MedicationFrequency = Literal[
    "daily",
    "twice_daily",
    "weekdays",
    "weekly",
    "monthly",
]


class MedicationCatalogItemRequest(BaseModel):
    """
    Optional metadata copied from the medication catalog used by the frontend.
    """

    id: str
    name: str
    active_substance: str
    strength: str
    dosage_form: str


class MedicationCatalogItemResponse(MedicationCatalogItemRequest):
    """
    Catalog metadata returned together with a saved medication entry.
    """


class MedicationCreateRequest(BaseModel):
    """
    Request body for creating a medication entry for one medical profile.
    """

    name: str = Field(min_length=1, max_length=255)
    dose: str = Field(min_length=1, max_length=100)
    intake_hour: int = Field(ge=0, le=23)
    intake_minute: int = Field(ge=0, le=59)
    second_intake_hour: Optional[int] = Field(default=None, ge=0, le=23)
    second_intake_minute: Optional[int] = Field(default=None, ge=0, le=59)
    frequency: MedicationFrequency = "daily"
    reminders_enabled: bool = True
    taken_date_keys: list[str] = Field(default_factory=list)
    catalog_item: Optional[MedicationCatalogItemRequest] = None
    created_at: Optional[datetime] = None


class MedicationUpdateRequest(BaseModel):
    """
    Request body for patching an existing medication entry.
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    dose: Optional[str] = Field(default=None, min_length=1, max_length=100)
    intake_hour: Optional[int] = Field(default=None, ge=0, le=23)
    intake_minute: Optional[int] = Field(default=None, ge=0, le=59)
    second_intake_hour: Optional[int] = Field(default=None, ge=0, le=23)
    second_intake_minute: Optional[int] = Field(default=None, ge=0, le=59)
    frequency: Optional[MedicationFrequency] = None
    reminders_enabled: Optional[bool] = None
    taken_date_keys: Optional[list[str]] = None
    catalog_item: Optional[MedicationCatalogItemRequest] = None


class MedicationResponse(BaseModel):
    """
    Medication entry returned to the frontend.
    """

    id: int
    profile_id: int
    name: str
    dose: str
    intake_hour: int
    intake_minute: int
    second_intake_hour: Optional[int] = None
    second_intake_minute: Optional[int] = None
    frequency: MedicationFrequency
    reminders_enabled: bool
    taken_date_keys: list[str]
    catalog_item: Optional[MedicationCatalogItemResponse] = None
    created_at: datetime
    updated_at: datetime


class MedicationDeleteResponse(BaseModel):
    """
    Response body returned after a medication entry has been soft-deleted.
    """

    message: str
