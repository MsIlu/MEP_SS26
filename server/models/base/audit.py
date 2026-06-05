from datetime import datetime, timezone
from pydantic import ConfigDict, Field
from models.base.base import BaseSchema

"""
Stellt automatische Zeitstempel für alle Datenmodelle bereit
"""
def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AuditInfo(BaseSchema):

    model_config = ConfigDict(validate_assignment=True)

    created_at: datetime = Field(
        default_factory=utc_now,
        description="Der exakte Erstellungszeitpunkt des Objekts im System (UTC)."
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        description="Der Zeitpunkt der letzten Modifikation oder des letzten Zugriffs (UTC)."
    )

    created_by: str | None = Field(
        default=None,
        description="Die Komponente oder Rolle, die das Objekt initial angelegt hat (z. B. 'frontend')."
    )

    updated_by: str | None = Field(
        default=None,
        description="Die Komponente oder Rolle, die das Objekt zuletzt aktualisiert hat."
    )