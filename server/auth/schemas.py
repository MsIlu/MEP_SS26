# Author: Ilu
# Created as part of the authentication and profile management implementation.
# This module defines request and response schemas for authentication endpoints.

from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """
    Request body for registering a new account and creating the initial main profile.
    """
    email: EmailStr
    password: str
    display_name: str
    date_of_birth: Optional[date] = None
    biological_sex: Optional[str] = None


class LoginRequest(BaseModel):
    """
    Request body for logging in with email and password.
    """
    email: EmailStr
    password: str


class AccountResponse(BaseModel):
    """
    Public account data returned to the frontend.

    Sensitive fields such as password_hash are intentionally excluded.
    """
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    """
    Public profile data returned after registration or login.

    The role field describes the current account's access rights for this profile.
    """
    id: int
    display_name: str
    profile_type: str
    role: Optional[str] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """
    Response body returned after successful registration or login.

    Contains the access token, public account data, and all accessible profiles.
    """
    access_token: str
    token_type: str = "bearer"
    account: AccountResponse
    profiles: list[ProfileResponse]


class MeResponse(BaseModel):
    """
    Response body for the currently authenticated account.
    """
    id: int
    email: EmailStr

    class Config:
        from_attributes = True