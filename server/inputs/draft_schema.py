from pydantic import BaseModel, Field


class SymptomDraftUpdateRequest(BaseModel):
    """
    Request body for updating symptoms in an input draft.
    """

    symptoms: list[str] = Field(default_factory=list)


class SymptomDraftResponse(BaseModel):
    """
    Response model returned to the frontend.
    """

    session_id: str
    symptoms: list[str]


class CancelDraftResponse(BaseModel):
    """
    Response model returned after cancelling a draft.
    """

    message: str
    session_id: str
