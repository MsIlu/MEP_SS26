from uuid import uuid4
from pydantic import Field, ConfigDict

from models.base.base import BaseSchema 
from models.base.audit import AuditInfo
from models.provenance.provenance_state import ProvenanceState


class Concern(BaseSchema):
    """
    Die Sorgen/Beschwerden des Patienten werden kategorisiert und
    nach Dringlichkeit eingestuft.
    """

    model_config = ConfigDict(validate_assignment=True)

    concern_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Eindeutige, automatisch generierte ID der Beschwerde."
    )

    description: str = Field(
        ...,
        description="Die detaillierte Beschreibung der Sorge oder Beschwerde im Freitext."
    )

    category: str | None = Field(
        default=None,
        description="Die medizinische Kategorie der Beschwerde (z. B. 'Kardiologie', 'Neurologie')."
    )

    priority: str | None = Field(
        default=None,
        description="Die Priorität oder Dringlichkeitsstufe der Beschwerde (z. B. 'low', 'medium', 'high')."
    )

    provenance: ProvenanceState = Field(
        default_factory=ProvenanceState,
        description="Herkunftsnachweis (Provenance), der die Beschwerde mit der Quellnachricht verknüpft."
    )

    audit: AuditInfo = Field(
        default_factory=AuditInfo,
        description="Automatische Zeitstempel und Komponenten-Protokolle für diese Beschwerde."
    )