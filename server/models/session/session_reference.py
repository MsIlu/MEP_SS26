"""

Es stellt die Verknüpfungsstruktur bereit, um klinische und administrative
Datenobjekte einer spezifischen Chat-Sitzung zuzuordnen.
"""

from datetime import datetime, timezone
from pydantic import Field, ConfigDict

# Absoluter Import zur Vermeidung von Pylance-Fehlern in VS Code
from models.base.base import BaseSchema


class SessionReference(BaseSchema):
    """
    Schema für die Referenzierung einer Sitzung.
    Dient als relationaler Anker für Datenbankeinträge.
    """

    model_config = ConfigDict(validate_assignment=True)

    session_id: str = Field(
        ...,
        description="Die eindeutige UUID der referenzierten Chat-Sitzung."
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Erstellungszeitpunkt der Referenz im System (UTC)."
    )

    last_updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Zeitpunkt der letzten Aktualisierung dieser Referenz (UTC)."
    )