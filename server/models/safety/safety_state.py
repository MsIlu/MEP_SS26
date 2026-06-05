from pydantic import Field, ConfigDict

from models.base.base import BaseSchema
from models.safety.red_flag import RedFlag
from models.safety.safety_event import SafetyEvent

"""
Verwaltet den aktuellen Sicherheitszustand einer Session

"""
class SafetyState(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    emergency_detected: bool = Field(
        default=False,
        description="True signalisiert einen akuten, medizinischen Notfall."
    )

    ai_response_blocked: bool = Field(
        default=False,
        description="True blockiert die reguläre LLM-Antwortgenerierung aus Sicherheitsgründen."
    )

    active_red_flags: list[RedFlag] = Field(
        default_factory=list,
        description="Liste aller im aktuellen Chatverlauf aktiv erkannten Alarmsymptome (Red Flags)."
    )

    safety_events: list[SafetyEvent] = Field(
        default_factory=list,
        description="Chronologisches Logbuch aller sicherheitsrelevanten System- und Guardrail-Ereignisse."
    )