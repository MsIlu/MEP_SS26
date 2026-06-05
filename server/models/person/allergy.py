from uuid import uuid4
from pydantic import Field, ConfigDict

from ..base.base import BaseSchema
from models.base.audit import AuditInfo

"""
Data model for patient reported allergies 
"""

class Allergy(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    allergy_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Eindeutige ID des Allergieeintrags."
    )

    substance: str = Field(
        ...,
        description="Die allergieauslösende Substanz (z. B. 'Penicillin', 'Ibuprofen')."
    )

    reaction: str | None = Field(
        default=None,
        description="Die vom Patienten beschriebene klinische Reaktion (z. B. 'Juckreiz', 'Ödem')."
    )

    severity: str | None = Field(
        default=None,
        description="Der Schweregrad der allergischen Reaktion (z. B. 'mild', 'moderate', 'severe')."
    )

    audit: AuditInfo = Field(
        default_factory=AuditInfo,
        description="Automatische Zeitstempel und Komponenten-Protokolle für diesen Allergieeintrag."
    )