from fastapi import APIRouter

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

router = APIRouter(prefix="/input-drafts", tags=["input-drafts"])


@router.get("/{session_id}", response_model=SymptomDraftResponse)
def get_draft(session_id: str):
    """
    Return the current symptom draft for a session.
    """

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=get_symptom_draft(session_id),
    )


@router.patch("/{session_id}", response_model=SymptomDraftResponse)
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


@router.delete("/{session_id}", response_model=CancelDraftResponse)
def cancel_draft(session_id: str):
    """
    Remove the draft for a session.
    """

    cancel_symptom_draft(session_id)

    return CancelDraftResponse(
        message="Draft cancelled successfully.",
        session_id=session_id,
    )
