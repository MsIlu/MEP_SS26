from typing import Literal
from pydantic import BaseModel

class ExtractionScope(BaseModel):
    """
    Defines which extraction pipelines should run.

    This is NOT medical content.
    It is routing only.
    """

    has_symptoms: bool = False
    has_medications: bool = False
    has_conditions: bool = False
    has_events: bool = False
    has_concerns: bool = False

    complexity: Literal["low", "medium", "high"] = "medium"