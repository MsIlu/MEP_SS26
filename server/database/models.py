# Author: Ilu
# Created and modified as part of the authentication and profile management implementation.
# This module defines database models for accounts, medical profiles, and account-profile access rights.
# SQLModel uses these classes to create the corresponding tables in PostgreSQL.

from datetime import datetime, date
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """
   Database model for an account used for authentication.

   Medical data must not be stored directly on this model.
   """
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)

    email: str = Field(index=True, unique=True, max_length=255)
    password_hash: str

    is_active: bool = Field(default=True)
    active_profile_id: Optional[int] = Field(default=None, foreign_key="profiles.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)

class Profile(SQLModel, table=True):
    """
   Database model for a medical profile.

   A profile represents the medical context of a person and can be connected
   to one or more accounts through AccountProfileAccess.
   """
    __tablename__ = "profiles"

    id: Optional[int] = Field(default=None, primary_key=True)

    display_name: str = Field(max_length=100)
    date_of_birth: Optional[date] = Field(default=None)
    biological_sex: Optional[str] = Field(default=None, max_length=30)
    height_cm: Optional[int] = Field(default=None)
    weight_kg: Optional[float] = Field(default=None)

    profile_type: str = Field(default="self", max_length=30)

    relevant_preconditions_summary: Optional[str] = Field(default=None)
    relevant_medications_summary: Optional[str] = Field(default=None)
    symptom_diary_summary: Optional[str] = Field(default=None)

    ai_disclaimer_accepted_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)


class SymptomDiaryEntry(SQLModel, table=True):
    """
   Database model for one symptom diary entry.

   Entries belong to a medical profile and mirror the symptom diary data
   structure used by the frontend.
   """
    __tablename__ = "symptom_diary_entries"

    id: Optional[int] = Field(default=None, primary_key=True)

    profile_id: int = Field(foreign_key="profiles.id", index=True)
    date: datetime = Field(index=True)
    symptom: str = Field(max_length=255)
    body_area: str = Field(default="", max_length=100)
    intensity: int
    note: str = Field(default="")

    created_at: datetime = Field(default_factory=datetime.utcnow)


class AccountProfileAccess(SQLModel, table=True):
    """
   Database model for access rights between accounts and profiles.

   This keeps profiles detachable from accounts and supports future transfer
   scenarios, for example when a child profile becomes an adult-owned profile.
   """
    __tablename__ = "acc_profile_access"

    id: Optional[int] = Field(default=None, primary_key=True)

    account_id: int = Field(foreign_key="users.id", index=True)
    profile_id: int = Field(foreign_key="profiles.id", index=True)

    role: str = Field(default="owner", max_length=30)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MedicationEntry(SQLModel, table=True):
    """
   Database model for one medication entry belonging to a profile.

   Entries are scoped to profiles so shared accounts only access medications
   through the existing profile permission model.
   """
    __tablename__ = "medication_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="profiles.id", index=True)

    name: str = Field(max_length=255)
    dose: str = Field(max_length=100)

    intake_hour: int
    intake_minute: int
    second_intake_hour: Optional[int] = Field(default=None)
    second_intake_minute: Optional[int] = Field(default=None)

    frequency: str = Field(default="daily", max_length=30)
    reminders_enabled: bool = Field(default=True)
    taken_date_keys: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )

    catalog_item_id: Optional[str] = Field(default=None, max_length=100)
    catalog_item_name: Optional[str] = Field(default=None, max_length=255)
    catalog_active_substance: Optional[str] = Field(default=None, max_length=255)
    catalog_strength: Optional[str] = Field(default=None, max_length=100)
    catalog_dosage_form: Optional[str] = Field(default=None, max_length=100)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)


class ChatHistory(SQLModel, table=True):
    """
    Persisted chat history for one medical profile.

    A history entry can be active while the chat is ongoing or completed after
    the chat produces a care recommendation.
    """
    __tablename__ = "chat_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="profiles.id", index=True)

    title: Optional[str] = Field(default=None, max_length=80)
    status: str = Field(default="completed", max_length=20, index=True)
    is_emergency: bool = Field(default=False)
    recommendation: str = Field(default="")
    next_steps: Optional[str] = Field(default=None)
    messages: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
