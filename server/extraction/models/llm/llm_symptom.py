from typing import Literal
from pydantic import BaseModel, Field

"""
    Additional symptom attributes extracted from user language.
"""
class LLMSymptomAttributes(BaseModel):
    severity: int | None = Field(default=None, ge=0, le=10)
    location: str | None = None
    radiation: str | None = None
    frequency: str | None = None

"""
    Raw temporal information extracted from natural language.

    These values intentionally remain text-based because
    user language is often vague or imprecise.
"""

class LLMTemporal(BaseModel):
    onset_text: str | None = None
    duration_text: str | None = None
    progression: Literal["improving", "worsening", "stable"] | None = None

"""
    Semantic assertion state of the extracted symptom.
    Note: Default status is confirmed.
"""
class LLMAssertion(BaseModel):
    status: Literal[
        "confirmed",
        "denied",
        "suspected",
        "uncertain",
        "historical",
    ] = "confirmed"

"""
    Structured symptom representation extracted by the LLM.

    This is not yet a finalized internal clinical object.
    It represents probabilistic structured extraction output.
"""
class LLMSymptom(BaseModel):
    id: str
    label: str

    attributes: LLMSymptomAttributes = Field(default_factory=LLMSymptomAttributes)
    temporal: LLMTemporal = Field(default_factory=LLMTemporal)
    assertion: LLMAssertion = Field(default_factory=LLMAssertion)