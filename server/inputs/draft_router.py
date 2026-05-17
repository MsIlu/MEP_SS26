from fastapi import APIRouter

from inputs.draft_service import (
    get_symptom_draft,
    update_symptom_draft,
    cancel_symptom_draft,
)

from inputs.draft_schema import (
    SymptomDraftUpdateRequest,
    SymptomDraftResponse,
    CancelDraftResponse,
)

router = APIRouter(
    prefix="/input-drafts",
    tags=["input-drafts"],
)


@router.get("/{session_id}", response_model=SymptomDraftResponse)
def get_draft(session_id: str):
    """
    Returns the current symptom draft for a session.
    """

    symptoms = get_symptom_draft(session_id)

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=symptoms,
    )


@router.patch("/{session_id}", response_model=SymptomDraftResponse)
def update_draft(
    session_id: str,
    request: SymptomDraftUpdateRequest,
):
    """
    Updates the symptom draft after user edits.
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
    cancel_symptom_draft(session_id)

    return CancelDraftResponse(
        message="Draft cancelled successfully.",
        session_id=session_id,
    )