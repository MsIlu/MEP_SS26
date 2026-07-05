# Author: Ilu
"""Profile HTTP routes; business logic is delegated to profiles.service.

Created as part of the authentication and profile management implementation.
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from auth.security import get_current_account, get_session
from database.models import User
from profiles.schemas import (
    ProfileCreateRequest,
    ProfileDeleteResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)
from profiles.service import (
    create_profile,
    delete_profile,
    get_profile,
    list_profiles,
    update_profile,
)


router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("", response_model=list[ProfileResponse])
def get_profiles(
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Return all non-deleted profiles accessible by the authenticated account.
    """
    return list_profiles(current_user=current_user, session=session)


@router.post("", response_model=ProfileResponse)
def post_profile(
        request: ProfileCreateRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Create a new medical profile for the authenticated account.
    """
    return create_profile(
        request=request,
        current_user=current_user,
        session=session,
    )


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile_by_id(
        profile_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Return a single profile if the authenticated account has access to it.
    """
    return get_profile(
        profile_id=profile_id,
        current_user=current_user,
        session=session,
    )


@router.patch("/{profile_id}", response_model=ProfileResponse)
def patch_profile(
        profile_id: int,
        request: ProfileUpdateRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Update a profile if the authenticated account has an editable role.
    """
    return update_profile(
        profile_id=profile_id,
        request=request,
        current_user=current_user,
        session=session,
    )


@router.delete("/{profile_id}", response_model=ProfileDeleteResponse)
def remove_profile(
        profile_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Soft-delete a profile if the authenticated account has a deletion role.
    """
    return delete_profile(
        profile_id=profile_id,
        current_user=current_user,
        session=session,
    )
