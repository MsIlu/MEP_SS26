from pydantic import Field, ConfigDict

from models.base.base import BaseSchema
from models.person.demographics import Demographics
from models.person.condition import Condition
from models.person.medication import Medication
from models.person.allergy import Allergy
from models.person.risk_factor import RiskFactor

"""
Bündelt Demografie, Vorerkrankungen, Medikationspläne,
Allergien und Risikofaktoren zu einem vollständigen Patientenprofil
"""

class PatientProfile(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    demographics: Demographics = Field(
        default_factory=Demographics,
        description="Biologische und demografische Basisdaten des Patienten."
    )

    chronic_conditions: list[Condition] = Field(
        default_factory=list,
        description="Liste aller bekannten chronischen oder langanhaltenden Vorerkrankungen."
    )

    medications: list[Medication] = Field(
        default_factory=list,
        description="Aktueller Medikationsplan bzw. eingenommene Dauermedikation."
    )

    allergies: list[Allergy] = Field(
        default_factory=list,
        description="Erfasste Allergien und Unverträglichkeiten zur Vermeidung von Kontraindikationen."
    )

    baseline_risk_factors: list[RiskFactor] = Field(
        default_factory=list,
        description="Generelle medizinische oder lebensstilbedingte Risikofaktoren des Patienten."
    )