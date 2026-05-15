from pydantic import Field

from ..base.base import BaseSchema

"""
Data model for patient information exceeding a single chat

parameters are not final

"""
class LongitudinalState(BaseSchema):
    recurring_symptoms: list[str] = Field(default_factory=list)

    frequent_visit_patterns: list[str] = Field(default_factory=list)

    derived_risk_patterns: list[str] = Field(default_factory=list)