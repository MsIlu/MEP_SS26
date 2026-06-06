# Author: Ilu
# Created and modified as part of the authentication and profile management implementation.
# This module defines database models for accounts, medical profiles, and account-profile access rights.
# SQLModel uses these classes to create the corresponding tables in PostgreSQL.

from datetime import datetime, date
from typing import Optional

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

    profile_type: str = Field(default="self", max_length=30)

    relevant_preconditions_summary: Optional[str] = Field(default=None)
    relevant_medications_summary: Optional[str] = Field(default=None)
    symptom_diary_summary: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)


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