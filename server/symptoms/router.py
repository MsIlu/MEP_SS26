from fastapi import APIRouter, Depends
from sqlmodel import Session

from auth.security import get_current_account, get_session
from database.models import User
from symptoms.schemas import SymptomCreateRequest, SymptomResponse
from symptoms.service import create_symptom_entry, list_symptom_entries


router = APIRouter(prefix="/profiles/{profile_id}/symptoms", tags=["symptoms"])


@router.get("", response_model=list[SymptomResponse])
def get_symptoms(
        profile_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Return symptom diary entries for a profile.
    """
    return list_symptom_entries(
        profile_id=profile_id,
        current_user=current_user,
        session=session,
    )


@router.post("", response_model=SymptomResponse)
def post_symptom(
        profile_id: int,
        request: SymptomCreateRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Store one symptom diary entry for a profile.
    """
    return create_symptom_entry(
        profile_id=profile_id,
        request=request,
        current_user=current_user,
        session=session,
    )
