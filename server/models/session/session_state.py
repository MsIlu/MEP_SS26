"""
Das zentrale Aggregat-Modell, das alle spezialisierten Teilzustände
(Klinisch, Konversation, Sicherheit, Metadaten) einer Sitzung bündelt.
"""

from pydantic import Field, ConfigDict

# Umstellung aller Imports auf absolute Pfade zur Eliminierung von Pylance-Warnungen
from models.base.base import BaseSchema
from models.session.session_participant import SessionParticipant
from models.session.session_subject import SessionSubject
from models.session.session_metadata import SessionMetadata
from models.clinical.clinical_state import ClinicalState
from models.safety.safety_state import SafetyState
from models.conversation.conversation_state import ConversationState
from models.provenance.provenance_state import ProvenanceState


class SessionState(BaseSchema):
    """
    Zentrales Zustandsschema einer Chat-Sitzung.
    Dient als primärer Einstiegspunkt für das Laden und Speichern im Session-Manager.
    """

    model_config = ConfigDict(validate_assignment=True)

    session_id: str = Field(
        ...,
        description="Eindeutige UUID der Chat-Sitzung."
    )

    person_id: str = Field(
        ...,
        description="Eindeutige ID des primären App-Nutzers."
    )

    participant: SessionParticipant = Field(
        default_factory=SessionParticipant,
        description="Informationen über den aktuellen Chat-Teilnehmer."
    )

    subject: SessionSubject = Field(
        default_factory=SessionSubject,
        description="Das medizinische Subjekt (der Patient), auf das sich die Sitzung bezieht."
    )

    clinical_state: ClinicalState = Field(
        default_factory=ClinicalState,
        description="Der erfasste klinische Zustand (Symptome, Dauer, Verlauf)."
    )

    safety_state: SafetyState = Field(
        default_factory=SafetyState,
        description="Sicherheitsrelevante Zustände (z. B. getriggerte Red Flags)."
    )

    conversation_state: ConversationState = Field(
        default_factory=ConversationState,
        description="Der Zustand der Konversationsführung (z. B. Chatverlauf-Metadaten)."
    )

    provenance_state: ProvenanceState = Field(
        default_factory=ProvenanceState,
        description="Herkunfts- und Protokollierungsdaten zur Nachvollziehbarkeit (Audit-Trail)."
    )

    metadata: SessionMetadata = Field(
        default_factory=SessionMetadata,
        description="Administrative Metadaten (Zeitstempel, Sprachkonfiguration)."
    )