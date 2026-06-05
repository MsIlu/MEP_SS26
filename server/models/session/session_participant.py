"""
Definiert die am Chat beteiligten Akteure und deren medizinische Rollen.
Ermöglicht die Unterscheidung zwischen dem Nutzer und dem eigentlichen Patienten.
"""

from pydantic import Field
from ..base.base import BaseSchema


class SessionParticipant(BaseSchema):
    """
    Schema zur Beschreibung eines Sitzungsteilnehmers.
    Verknüpft die technische Session mit den realen Personenprofilen aus der Datenbank.
    """

    participant_id: str = Field(
        ...,
        description="Eindeutige Identifikationsnummer des Teilnehmers in dieser Sitzung."
    )

    person_id: str | None = Field(
        default=None,
        description="Optionale Verknüpfung zur ID der realen Person in der Datenbank."
    )

    role: str = Field(
        ...,
        description="Die Rolle des Teilnehmers (z. B. 'patient', 'relative', 'doctor')."
    )

    class ConfigDict:
        """Pydantic-Konfiguration für strikte Validierung."""
        validate_assignment = True