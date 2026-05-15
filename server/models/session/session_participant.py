from ..base.base import BaseSchema

"""
Data model to describe the participants within a session
Used to describe wether the patient is referring to himself or someone else
"""

class SessionParticipant(BaseSchema):
    participant_id: str

    person_id: str | None = None

    role: str