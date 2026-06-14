from typing import Literal

from extraction.models.system.baseSchema import BaseSchema


class SymptomConfirmation(BaseSchema):
    """
    A symptom from an assistant follow-up question resolved by the user's reply.
    """

    label: str
    status: Literal["confirmed", "denied", "uncertain"]
    evidence: str


class SymptomConfirmationResult(BaseSchema):
    """
    Structured result for symptom confirmation from question-answer context.
    """

    symptoms: list[SymptomConfirmation]
