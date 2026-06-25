# Author: Ilu
# Created as part of the authentication and profile management implementation.
# This module defines authentication HTTP routes and delegates business logic to auth.service.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from auth.schemas import AuthResponse, LoginRequest, MeResponse, RegisterRequest
from auth.security import (
    create_access_token,
    get_current_account,
    get_session,
    verify_password,
)
from auth.service import deactivate_account, login_account, register_account
from database.models import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register(
        request: RegisterRequest,
        session: Session = Depends(get_session),
):
    """
    Register a new account and automatically create its main profile.
    """
    return register_account(request=request, session=session)


@router.post("/login", response_model=AuthResponse)
def login(
        request: LoginRequest,
        session: Session = Depends(get_session),
):
    """
    Log in with email and password using the JSON API used by the frontend.
    """
    return login_account(request=request, session=session)


@router.post("/token")
def login_for_swagger(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session),
):
    """
    Log in using OAuth2 form data so Swagger's Authorize button can obtain a token.

    The frontend should use /auth/login.
    This endpoint exists mainly for interactive API testing in Swagger UI.
    """
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    token = create_access_token(account_id=user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=MeResponse)
def get_me(
        current_user: User = Depends(get_current_account),
):
    """
    Return the currently authenticated account.
    """
    return MeResponse.model_validate(current_user)


@router.delete("/me")
def delete_me(
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Soft-delete the currently authenticated account.
    """
    return deactivate_account(current_user=current_user, session=session)