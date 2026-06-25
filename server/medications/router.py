# HTTP routes for profile-scoped medication entries.

from fastapi import APIRouter, Depends
from sqlmodel import Session

from auth.security import get_current_account, get_session
from database.models import User
from medications.schemas import (
    MedicationCreateRequest,
    MedicationDeleteResponse,
    MedicationResponse,
    MedicationUpdateRequest,
)
from medications.service import (
    create_medication,
    delete_medication,
    get_medication,
    list_medications,
    update_medication,
)


router = APIRouter(
    prefix="/profiles/{profile_id}/medications",
    tags=["medications"],
)


@router.get("", response_model=list[MedicationResponse])
def get_profile_medications(
        profile_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Return medication entries for one accessible medical profile.
    """
    return list_medications(
        profile_id=profile_id,
        current_user=current_user,
        session=session,
    )


@router.post("", response_model=MedicationResponse)
def post_profile_medication(
        profile_id: int,
        request: MedicationCreateRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Create one medication entry for a medical profile.
    """
    return create_medication(
        profile_id=profile_id,
        request=request,
        current_user=current_user,
        session=session,
    )


@router.get("/{medication_id}", response_model=MedicationResponse)
def get_profile_medication_by_id(
        profile_id: int,
        medication_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Return one medication entry from a medical profile.
    """
    return get_medication(
        profile_id=profile_id,
        medication_id=medication_id,
        current_user=current_user,
        session=session,
    )


@router.patch("/{medication_id}", response_model=MedicationResponse)
def patch_profile_medication(
        profile_id: int,
        medication_id: int,
        request: MedicationUpdateRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Update one medication entry from a medical profile.
    """
    return update_medication(
        profile_id=profile_id,
        medication_id=medication_id,
        request=request,
        current_user=current_user,
        session=session,
    )


@router.delete("/{medication_id}", response_model=MedicationDeleteResponse)
def remove_profile_medication(
        profile_id: int,
        medication_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Soft-delete one medication entry from a medical profile.
    """
    return delete_medication(
        profile_id=profile_id,
        medication_id=medication_id,
        current_user=current_user,
        session=session,
    )
