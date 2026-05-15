from pydantic import Field

from .base import BaseSchema
from .patient_profile import PatientProfile
from .session_reference import SessionReference
from .longitudinal_state import LongitudinalState


class Person(BaseSchema):
    person_id: str

    patient_profile: PatientProfile = Field(default_factory=PatientProfile)

    sessions: list[SessionReference] = Field(default_factory=list)

    longitudinal_state: LongitudinalState = Field(default_factory=LongitudinalState)