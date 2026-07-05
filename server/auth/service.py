# Author: Ilu
"""Authentication business logic (registration, login, account deactivation),
kept separate from HTTP routing.

Created as part of the authentication and profile management implementation.
"""

from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from auth.schemas import AccountResponse, AuthResponse, LoginRequest, ProfileResponse, RegisterRequest
from auth.security import create_access_token, hash_password, verify_password
from database.models import AccountProfileAccess, Profile, User


def register_account(request: RegisterRequest, session: Session) -> AuthResponse:
    """
    Register a new account and create its initial main profile.

    This function:
    - checks whether the email is already registered,
    - hashes the password,
    - creates the user account,
    - creates the user's main profile,
    - links the account and profile with the owner role,
    - returns an access token and profile information.
    """
    existing_user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    profile = Profile(
        display_name=request.display_name,
        date_of_birth=request.date_of_birth,
        biological_sex=request.biological_sex,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        relevant_preconditions_summary=request.relevant_preconditions_summary,
        relevant_medications_summary=request.relevant_medications_summary,
        symptom_diary_summary=request.symptom_diary_summary,
        profile_type="self",
    )

    session.add(profile)
    session.commit()
    session.refresh(profile)

    access = AccountProfileAccess(
        account_id=user.id,
        profile_id=profile.id,
        role="owner",
    )

    session.add(access)

    user.active_profile_id = profile.id
    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()
    session.refresh(user)
    session.refresh(profile)

    token = create_access_token(account_id=user.id)

    return AuthResponse(
        access_token=token,
        account=AccountResponse.model_validate(user),
        profiles=[
            ProfileResponse(
                id=profile.id,
                display_name=profile.display_name,
                profile_type=profile.profile_type,
                ai_disclaimer_accepted_at=profile.ai_disclaimer_accepted_at,
                role=access.role,
            )
        ],
    )


def login_account(request: LoginRequest, session: Session) -> AuthResponse:
    """
    Authenticate an account with email and password.

    This function:
    - validates the account credentials,
    - rejects inactive accounts,
    - loads all non-deleted profiles accessible by the account,
    - returns an access token and the accessible profiles.
    """
    user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    profile_rows = session.exec(
        select(Profile, AccountProfileAccess)
        .join(AccountProfileAccess, AccountProfileAccess.profile_id == Profile.id)
        .where(AccountProfileAccess.account_id == user.id)
        .where(Profile.deleted_at.is_(None))
        .order_by(
            (Profile.profile_type != "self").asc(),
            Profile.created_at.asc(),
            Profile.id.asc(),
        )
    ).all()

    profiles = [
        ProfileResponse(
            id=profile.id,
            display_name=profile.display_name,
            profile_type=profile.profile_type,
            ai_disclaimer_accepted_at=profile.ai_disclaimer_accepted_at,
            role=access.role,
        )
        for profile, access in profile_rows
    ]

    token = create_access_token(account_id=user.id)

    return AuthResponse(
        access_token=token,
        account=AccountResponse.model_validate(user),
        profiles=profiles,
    )


def deactivate_account(current_user: User, session: Session) -> dict:
    """
    Soft-delete an account and profiles managed only by this account.

    Shared profiles remain available to their other accounts. Health records
    stay in the database and become inaccessible through soft-deleted profiles.
    """
    deleted_at = datetime.utcnow()
    accesses = session.exec(
        select(AccountProfileAccess).where(
            AccountProfileAccess.account_id == current_user.id
        )
    ).all()

    for access in accesses:
        shared_access = session.exec(
            select(AccountProfileAccess)
            .where(AccountProfileAccess.profile_id == access.profile_id)
            .where(AccountProfileAccess.account_id != current_user.id)
        ).first()

        if shared_access is None:
            profile = session.get(Profile, access.profile_id)
            if profile is not None and profile.deleted_at is None:
                profile.deleted_at = deleted_at
                profile.updated_at = deleted_at
                session.add(profile)

    current_user.is_active = False
    current_user.active_profile_id = None
    current_user.deleted_at = deleted_at
    current_user.updated_at = deleted_at

    session.add(current_user)
    session.commit()

    return {"message": "Account deleted successfully."}
