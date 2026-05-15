from pydantic import Field

from .base import BaseSchema
from .symptom import Symptom
from .concern import Concern
from .clinical_fact import ClinicalFact
from .recommendation import Recommendation


class ClinicalState(BaseSchema):
    active_symptoms: list[Symptom] = Field(default_factory=list)

    concerns: list[Concern] = Field(default_factory=list)

    extracted_facts: list[ClinicalFact] = Field(default_factory=list)

    recommendation: Recommendation | None = None