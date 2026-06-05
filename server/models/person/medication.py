from uuid import uuid4
from pydantic import Field, ConfigDict

from models.base.base import BaseSchema
from models.base.audit import AuditInfo

"""
Zeigt die eingenommenen Medikamente eines Patienten
"""

class Medication(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    medication_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Eindeutige ID des Medikamenteneintrag."
    )

    name: str = Field(
        ...,
        description="Der Name des Medikaments oder des Wirkstoffs (z. B. 'Metformin')."
    )

    dosage: str | None = Field(
        default=None,
        description="Die Dosierung des Medikaments (z. B. '500 mg' oder '20 Tropfen')."
    )

    frequency: str | None = Field(
        default=None,
        description="Die Einnahmehäufigkeit (z. B. '1-0-1-0' oder 'einmal täglich abends')."
    )

    audit: AuditInfo = Field(
        default_factory=AuditInfo,
        description="Automatische Zeitstempel und Komponenten-Protokolle für diesen Medikamenteneintrag."
    )