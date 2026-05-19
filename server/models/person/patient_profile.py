from pydantic import Field

from .base import BaseSchema
from .demographics import Demographics
from .condition import Condition
from .medication import Medication
from .allergy import Allergy
from .risk_factor import RiskFactor


class PatientProfile(BaseSchema):
    demographics: Demographics = Field(default_factory=Demographics)

    chronic_conditions: list[Condition] = Field(default_factory=list)

    medications: list[Medication] = Field(default_factory=list)

    allergies: list[Allergy] = Field(default_factory=list)

    baseline_risk_factors: list[RiskFactor] = Field(default_factory=list)