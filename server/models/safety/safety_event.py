from uuid import uuid4
from datetime import datetime
from pydantic import Field, ConfigDict
from models.base.base import BaseSchema
from models.base.audit import utc_now

"""
Stellt sicher, dass Systemanomalien und Manipulationsversuche auditsicher aufgezeichnet werden.
"""

class SafetyEvent(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    event_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Eindeutige ID des Sicherheitsereignisses."
    )

    event_type: str = Field(
        ...,
        description="Der Typ des Ereignisses (z. B. 'prompt_injection', 'guardrail_violation', 'system_error')."
    )

    description: str = Field(
        ...,
        description="Detaillierte Beschreibung des Vorfalls oder der Systemanomalie."
    )

    timestamp: datetime = Field(
        default_factory=utc_now,
        description="Der exakte Generierungszeitpunkt des Ereignisses in UTC."
    )