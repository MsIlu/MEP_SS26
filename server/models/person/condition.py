from uuid import uuid4
from pydantic import Field, ConfigDict

from models.base.base import BaseSchema 
from models.base.audit import AuditInfo
from models.clinical.coding import Coding

"""
Repräsentiert eine langanhaltende oder chronische medizinische Diagnose
"""
class Condition(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    condition_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Eindeutige, automatisch generierte ID des Erkrankungseintrags."
    )

    name: str = Field(
        ...,
        description="Der klinische Name der Erkrankung oder Diagnose (z. B. 'Asthma bronchiale')."
    )

    coding: Coding | None = Field(
        default=None,
        description="Die standardisierte medizinische Codierung (z. B. ICD-10 Code wie 'E11' für Diabetes)."
    )

    chronic: bool = Field(
        default=True,
        description="True, wenn es sich um eine chronische oder persistierende Erkrankung handelt."
    )

    audit: AuditInfo = Field(
        default_factory=AuditInfo,
        description="Automatische Zeitstempel und Komponenten-Protokolle für diesen Erkrankungseintrag."
    )