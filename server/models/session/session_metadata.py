"""
Session Metadata Schema 
Definiert zeitliche und sprachliche Metadaten für eine Chat-Sitzung.
Nutzt Pydantic v2 Core-Features für zeitzonensichere Validierung.
"""

from datetime import datetime, timezone
from pydantic import Field, ConfigDict
from models.base.base import BaseSchema


class SessionMetadata(BaseSchema):
    """
    Schema zur Verwaltung von Sitzungsmetadaten.
    Garantisiert konsistente Zeitstempel und Systemkonfigurationen per Session.
    """

    # Aktiviert die strikte Validierung bei nachträglichen Zuweisungen im Code
    model_config = ConfigDict(validate_assignment=True) 

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Der exakte, zeitzonensichere Erstellungszeitpunkt der Session (UTC)."
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Der Zeitpunkt der letzten Interaktion innerhalb dieser Session (UTC)."
    )

    language: str = Field(
        default="de",
        max_length=5,
        description="ISO-Sprachcode für die Sitzung (z. B. 'de', 'en')."
    )

    model_version: str | None = Field(
        default=None,
        description="Die exakte Version des genutzten LLMs (z. B. 'medgemma:27b')."
    )

    