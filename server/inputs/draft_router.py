from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from auth.security import get_optional_current_account, get_session
from database.models import User
from inputs.draft_schema import (
    CancelDraftResponse,
    SymptomDraftResponse,
    SymptomDraftUpdateRequest,
)
from inputs.draft_service import (
    cancel_symptom_draft,
    get_symptom_draft,
    update_symptom_draft,
)
from profiles.service import get_profile_access_role

router = APIRouter(prefix="/input-drafts", tags=["input-drafts"])
_session_manager = None


def set_session_manager(session_manager) -> None:
    global _session_manager
    _session_manager = session_manager


def require_draft_session_access(
    session_id: str,
    current_user: User | None = Depends(get_optional_current_account),
    session: Session = Depends(get_session),
) -> None:
    if _session_manager is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Input draft session manager is not configured.",
        )

    if not _session_manager.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )

    profile_id = _session_manager.get_profile_id(session_id)

    if profile_id is None:
        return

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required for profile draft requests.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=session,
    )


@router.get(
    "/{session_id}",
    response_model=SymptomDraftResponse,
    dependencies=[Depends(require_draft_session_access)],
)
def get_draft(session_id: str):
    """
    Return the current symptom draft for a session.
    """

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=get_symptom_draft(session_id),
    )


@router.patch(
    "/{session_id}",
    response_model=SymptomDraftResponse,
    dependencies=[Depends(require_draft_session_access)],
)
def update_draft(
    session_id: str,
    request: SymptomDraftUpdateRequest,
):
    """
    Update the symptom draft after user edits.
    """

    updated_symptoms = update_symptom_draft(
        session_id=session_id,
        symptoms=request.symptoms,
    )

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=updated_symptoms,
    )


@router.delete(
    "/{session_id}",
    response_model=CancelDraftResponse,
    dependencies=[Depends(require_draft_session_access)],
)
def cancel_draft(session_id: str):
    """
    Remove the draft for a session.
    """

    cancel_symptom_draft(session_id)

    return CancelDraftResponse(
        message="Draft cancelled successfully.",
        session_id=session_id,
    )
