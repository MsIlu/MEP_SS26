# Author: Ilu
# Created as part of the authentication and profile management implementation.
# This module defines request and response schemas for profile endpoints.

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ProfileCreateRequest(BaseModel):
    """
    Request body for creating a new medical profile for the authenticated account.
    """

    display_name: str
    date_of_birth: Optional[date] = None
    biological_sex: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    profile_type: str = "other"
    relevant_preconditions_summary: Optional[str] = None
    relevant_medications_summary: Optional[str] = None
    symptom_diary_summary: Optional[str] = None
    ai_disclaimer_accepted_at: Optional[datetime] = None


class ProfileUpdateRequest(BaseModel):
    """
    Request body for updating an existing medical profile.

    All fields are optional so the frontend can update only selected fields.
    """

    display_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    biological_sex: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    profile_type: Optional[str] = None
    relevant_preconditions_summary: Optional[str] = None
    relevant_medications_summary: Optional[str] = None
    symptom_diary_summary: Optional[str] = None
    ai_disclaimer_accepted_at: Optional[datetime] = None


class ProfileResponse(BaseModel):
    """
    Public profile data returned to the frontend.

    The role field describes the authenticated account's permissions for this profile.
    """

    id: int
    display_name: str
    date_of_birth: Optional[date] = None
    biological_sex: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    profile_type: str
    relevant_preconditions_summary: Optional[str] = None
    relevant_medications_summary: Optional[str] = None
    symptom_diary_summary: Optional[str] = None
    ai_disclaimer_accepted_at: Optional[datetime] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True


class ProfileDeleteResponse(BaseModel):
    """
    Response body returned after a profile has been soft-deleted.
    """

    message: str
