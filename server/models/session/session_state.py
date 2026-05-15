from pydantic import Field

from ..session.session_subject import SessionSubject
from ..session.session_participant import SessionParticipant
from ..base.base import BaseSchema
from ..clinical.clinical_state import ClinicalState
from ..safety.safety_state import SafetyState
from ..conversation.conversation_state import ConversationState
from ..provenance.provenance_state import ProvenanceState
from .session_metadata import SessionMetadata

"""
Data Model for a single session
Holds all relevant information regarding this session
"""
class SessionState(BaseSchema):
    session_id: str

    person_id: str

    participant: SessionParticipant = Field(default_factory=SessionParticipant)

    subject: SessionSubject = Field(default_factory=SessionSubject)

    clinical_state: ClinicalState = Field(default_factory=ClinicalState)

    safety_state: SafetyState = Field(default_factory=SafetyState)

    conversation_state: ConversationState = Field(default_factory=ConversationState)

    provenance_state: ProvenanceState = Field(default_factory=ProvenanceState)

    metadata: SessionMetadata = Field(default_factory=SessionMetadata)