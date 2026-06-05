from pydantic import Field, ConfigDict

from models.base.base import BaseSchema
from models.person.patient_profile import PatientProfile
from models.session.session_reference import SessionReference  
from models.longitudinal.longitudinal_state import LongitudinalState

"""
Es fasst die medizinischen Stammdaten, administrative Identifikation und
die historische Chat-Übersicht zusammen.
"""

class Person(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    person_id: str = Field(
        ...,
        description="Eindeutige ID der Person (z. B. PostgreSQL-User-UUID oder Matrikel-Dummy)."
    )

    patient_profile: PatientProfile = Field(
        default_factory=PatientProfile,
        description="Die Patientenakte (Stammdaten, Allergien, Vorerkrankungen)."
    )

    sessions: list[SessionReference] = Field(
        default_factory=list,
        description="Chronologische Liste von Referenzen auf alle vergangenen und aktiven Chat-Sessions."
    )

    longitudinal_state: LongitudinalState = Field(
        default_factory=LongitudinalState,
        description="Die berechneten Langzeit- und Risikomuster über alle Sessions hinweg."
    )