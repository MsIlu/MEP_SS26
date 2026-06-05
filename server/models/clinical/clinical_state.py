from pydantic import Field, ConfigDict

# Umstellung auf absolute Imports zur Vermeidung von Pylance-Fehlern
from models.base.base import BaseSchema
from models.clinical.symptom import Symptom
from models.clinical.concern import Concern
from models.clinical.clinical_fact import ClinicalFact
from models.clinical.recommendation import Recommendation


class ClinicalState(BaseSchema):
    """
    Repräsentiert den gesamten klinischen Zustand einer Session.
    Dient dem Backend als Übersicht über den aktuellen Patientenstatus.
    """
    model_config = ConfigDict(validate_assignment=True)

    active_symptoms: list[Symptom] = Field(
        default_factory=list,
        description="Liste aller aktiv erfassten Symptome des Patienten."
    )

    concerns: list[Concern] = Field(
        default_factory=list,
        description="Liste der Kernbeschwerden oder medizinischen Sorgen des Nutzers."
    )

    extracted_facts: list[ClinicalFact] = Field(
        default_factory=list,
        description="Sammlung aller atomar aus dem Chat extrahierten klinischen Fakten."
    )

    recommendation: Recommendation | None = Field(
        default=None,
        description="Die aus den Symptomen generierte klinische Handlungsempfehlung (falls vorhanden)."
    )