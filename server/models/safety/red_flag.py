from uuid import uuid4
from pydantic import Field, ConfigDict 

from ..base.base import BaseSchema
from ..provenance.provenance import Provenance

"""
Definiert das Gerüst für die Red-Flag Logik zur Erkennung und
Protokollierung der Alarmsymptome und akuter Notfallsituationen im Chatverlauf.
"""
class RedFlag(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    red_flag_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Eindeutige ID des Alarmsymptoms."
    )

    rule_id: str = Field(
        ...,
        description="Die Kennung der spezifischen Sicherheits- oder Wissensregel, die ausgelöst wurde (z. B. 'RF_CARDIO_001')."
    )

    name: str = Field(
        ...,
        description="Der klinische Name der Red Flag (z. B. ' Sehr starke Kopfschmerzen', 'Akutes Abdomen')."
    )

    severity: str = Field(
        ...,
        description="Die Dringlichkeitsstufe des Alarms (z. B. 'high', 'critical', 'immediate_emergency')."
    )

    category: str | None = Field(
        default=None,
        description="Die medizinische Kategorie der Red Flag (z. B. 'Neurologie', 'Kardiologie')."
    )

    action: str | None = Field(
        default=None,
        description="Die erzwungene Handlungsanweisung für das Frontend (z. B. '112 anrufen', 'Sofortige Vorstellung Rettungsstelle')."
    )

    matched_keywords: list[str] = Field(
        default_factory=list,
        description="Liste der spezifischen Schlüsselwörter aus dem Chat, die zum Match geführt haben."
    )

    provenance: Provenance = Field(
        default_factory=Provenance,
        description="Nachweis, der die Red Flag mit der exakten Nachricht des Patienten verknüpft."
    )