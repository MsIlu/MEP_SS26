from pydantic import Field

from ..base.base import BaseSchema
from .red_flag import RedFlag
from .safety_event import SafetyEvent

"""
Data model to store information about safety events within a session

"""
class SafetyState(BaseSchema):
    emergency_detected: bool = False

    ai_response_blocked: bool = False

    active_red_flags: list[RedFlag] = Field(default_factory=list)

    safety_events: list[SafetyEvent] = Field(default_factory=list)