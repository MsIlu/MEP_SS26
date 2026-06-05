"""
Definiert den eigentlichen Patienten einer Sitzung,
falls der Nutzer der App stellvertretend für eine andere Person chattet.
"""

from pydantic import Field, ConfigDict
from models.base.base import BaseSchema


class SessionSubject(BaseSchema):
    """
    Schema zur Beschreibung des Patientensubjekts.
    Ermöglicht die stellvertretende Symptomerfassung für Angehörige oder Dritte.
    """

    model_config = ConfigDict(validate_assignment=True)

    person_id: str | None = Field(
        default=None,
        description="Optionale, eindeutige ID des Patienten aus der Datenbank."
    )

    temporary_label: str | None = Field(
        default=None,
        description="Temporäre Bezeichnung während des Chats (z. B. 'Tochter', 'Fremder')."
    )

    relationship_to_user: str | None = Field(
        default=None,
        description="Das genaue Verwandtschafts- oder Beziehungsverhältnis zum App-Nutzer."
    )