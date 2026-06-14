# Author: Ilu
# Created as part of the authentication and profile management implementation.
# This module contains business logic and authorization checks for medical profiles.

from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from database.models import AccountProfileAccess, Profile, User
from profiles.schemas import (
    ProfileCreateRequest,
    ProfileDeleteResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)


EDIT_ROLES = {"owner", "guardian", "editor"}
DELETE_ROLES = {"owner", "guardian"}


def get_profile_access_role(account_id: int, profile_id: int, session: Session) -> str:
    """
    Return the account's role for a profile.

    Raises 404 if the profile does not exist or has been soft-deleted.
    Raises 403 if the account has no access to the profile.
    """
    profile = session.get(Profile, profile_id)

    if profile is None or profile.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )

    access = session.exec(
        select(AccountProfileAccess)
        .where(AccountProfileAccess.account_id == account_id)
        .where(AccountProfileAccess.profile_id == profile_id)
    ).first()

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this profile.",
        )

    return access.role


def require_profile_role(
        account_id: int,
        profile_id: int,
        allowed_roles: set[str],
        session: Session,
) -> str:
    """
    Ensure that an account has one of the required roles for a profile.

    Returns the role if access is allowed.
    Raises 403 if the role is insufficient.
    """
    role = get_profile_access_role(
        account_id=account_id,
        profile_id=profile_id,
        session=session,
    )

    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )

    return role


def list_profiles(current_user: User, session: Session) -> list[ProfileResponse]:
    """
    Return all non-deleted profiles accessible by the authenticated account.
    """
    rows = session.exec(
        select(Profile, AccountProfileAccess)
        .join(AccountProfileAccess, AccountProfileAccess.profile_id == Profile.id)
        .where(AccountProfileAccess.account_id == current_user.id)
        .where(Profile.deleted_at.is_(None))
    ).all()

    return [
        ProfileResponse(
            id=profile.id,
            display_name=profile.display_name,
            date_of_birth=profile.date_of_birth,
            biological_sex=profile.biological_sex,
            profile_type=profile.profile_type,
            relevant_preconditions_summary=profile.relevant_preconditions_summary,
            relevant_medications_summary=profile.relevant_medications_summary,
            symptom_diary_summary=profile.symptom_diary_summary,
            ai_disclaimer_accepted_at=profile.ai_disclaimer_accepted_at,
            role=access.role,
        )
        for profile, access in rows
    ]


def create_profile(
        request: ProfileCreateRequest,
        current_user: User,
        session: Session,
) -> ProfileResponse:
    """
    Create a new medical profile and link it to the authenticated account.

    The assigned role depends on the profile type.
    """
    profile = Profile(
        display_name=request.display_name,
        date_of_birth=request.date_of_birth,
        biological_sex=request.biological_sex,
        profile_type=request.profile_type,
        relevant_preconditions_summary=request.relevant_preconditions_summary,
        relevant_medications_summary=request.relevant_medications_summary,
        symptom_diary_summary=request.symptom_diary_summary,
        ai_disclaimer_accepted_at=request.ai_disclaimer_accepted_at,
    )

    session.add(profile)
    session.commit()
    session.refresh(profile)

    if request.profile_type == "self":
        role = "owner"
    elif request.profile_type == "child":
        role = "guardian"
    elif request.profile_type == "relative":
        role = "guardian"
    else:
        role = "editor"

    access = AccountProfileAccess(
        account_id=current_user.id,
        profile_id=profile.id,
        role=role,
    )

    session.add(access)
    session.commit()

    return ProfileResponse(
        id=profile.id,
        display_name=profile.display_name,
        date_of_birth=profile.date_of_birth,
        biological_sex=profile.biological_sex,
        profile_type=profile.profile_type,
        relevant_preconditions_summary=profile.relevant_preconditions_summary,
        relevant_medications_summary=profile.relevant_medications_summary,
        symptom_diary_summary=profile.symptom_diary_summary,
        ai_disclaimer_accepted_at=profile.ai_disclaimer_accepted_at,
        role=role,
    )


def get_profile(
        profile_id: int,
        current_user: User,
        session: Session,
) -> ProfileResponse:
    """
    Return a single profile if the authenticated account has access to it.
    """
    role = get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=session,
    )

    profile = session.get(Profile, profile_id)

    return ProfileResponse(
        id=profile.id,
        display_name=profile.display_name,
        date_of_birth=profile.date_of_birth,
        biological_sex=profile.biological_sex,
        profile_type=profile.profile_type,
        relevant_preconditions_summary=profile.relevant_preconditions_summary,
        relevant_medications_summary=profile.relevant_medications_summary,
        symptom_diary_summary=profile.symptom_diary_summary,
        ai_disclaimer_accepted_at=profile.ai_disclaimer_accepted_at,
        role=role,
    )


def update_profile(
        profile_id: int,
        request: ProfileUpdateRequest,
        current_user: User,
        session: Session,
) -> ProfileResponse:
    """
    Update a profile if the authenticated account has an editable role.
    """
    role = require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )

    profile = session.get(Profile, profile_id)

    update_data = request.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        setattr(profile, field_name, value)

    profile.updated_at = datetime.utcnow()

    session.add(profile)
    session.commit()
    session.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        display_name=profile.display_name,
        date_of_birth=profile.date_of_birth,
        biological_sex=profile.biological_sex,
        profile_type=profile.profile_type,
        relevant_preconditions_summary=profile.relevant_preconditions_summary,
        relevant_medications_summary=profile.relevant_medications_summary,
        symptom_diary_summary=profile.symptom_diary_summary,
        ai_disclaimer_accepted_at=profile.ai_disclaimer_accepted_at,
        role=role,
    )


def delete_profile(
        profile_id: int,
        current_user: User,
        session: Session,
) -> ProfileDeleteResponse:
    """
    Soft-delete a profile if the authenticated account has a deletion role.

    The profile row remains in the database but is hidden from normal profile queries.
    """
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=DELETE_ROLES,
        session=session,
    )

    profile = session.get(Profile, profile_id)
    profile.deleted_at = datetime.utcnow()
    profile.updated_at = datetime.utcnow()

    if current_user.active_profile_id == profile.id:
        current_user.active_profile_id = None
        current_user.updated_at = datetime.utcnow()
        session.add(current_user)

    session.add(profile)
    session.commit()

    return ProfileDeleteResponse(message="Profile deleted successfully.")
