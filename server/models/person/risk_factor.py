from uuid import uuid4
from pydantic import Field, ConfigDict

from models.base.base import BaseSchema
from models.base.audit import AuditInfo

"""
Erfasst und strukturiert die allgemeinen und chronischen Risikofaktoren des Patienten
"""


class RiskFactor(BaseSchema):
    
    model_config = ConfigDict(validate_assignment=True)

    risk_factor_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Eindeutige, automatisch generierte ID des Risikofaktors."
    )

    name: str = Field(
        ...,
        description="Der Name des Risikofaktors (z. B. 'Raucherstatus', 'Alkoholkonsum', 'Adipositas')."
    )

    value: str | None = Field(
        default=None,
        description="Optionale quantitative oder qualitative Ausprägung des Risikos (z. B. '10 Zigaretten/Tag')."
    )

    audit: AuditInfo = Field(
        default_factory=AuditInfo,
        description="Automatische Zeitstempel und Komponenten-Protokolle für diesen Risikofaktor."
    )