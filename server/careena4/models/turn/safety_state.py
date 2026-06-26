from __future__ import annotations

from enum import Enum

from pydantic import Field

from careena4.models.common import PipelineModel


class SafetyRedFlagStatus(str, Enum):
    NONE = "none"
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    CLARIFIED_NEGATIVE = "clarified_negative"


class SafetyAction(str, Enum):
    NONE = "none"
    ASK_SAFETY_CLARIFICATION = "ask_safety_clarification"
    EMERGENCY = "emergency"


class SafetyClarificationOutcome(str, Enum):
    CONFIRMED_RED_FLAG = "confirmed_red_flag"
    CLEARED_RED_FLAG = "cleared_red_flag"
    STILL_UNCLEAR = "still_unclear"
    CONFIRMED_EMERGENCY = "confirmed_emergency"
    INVALID_ANSWER = "invalid_answer"


class SafetyState(PipelineModel):
    checked_sources: list[str] = Field(default_factory=list)
    red_flag_detected: bool = False
    red_flag_status: SafetyRedFlagStatus = SafetyRedFlagStatus.NONE
    action: SafetyAction = SafetyAction.NONE
    severity: str | None = None
    evidence_terms: list[str] = Field(default_factory=list)
    clarification_question_code: str | None = None
    trace_notes: list[str] = Field(default_factory=list)

    @property
    def requires_emergency_response(self) -> bool:
        return self.action == SafetyAction.EMERGENCY

    @property
    def requires_safety_clarification(self) -> bool:
        return (
            self.red_flag_status in {SafetyRedFlagStatus.SUSPECTED, SafetyRedFlagStatus.CONFIRMED}
            and self.action == SafetyAction.ASK_SAFETY_CLARIFICATION
        )


class SafetyClarificationResolution(PipelineModel):
    outcome: SafetyClarificationOutcome
    safety_state: SafetyState
    clear_pending_clarification: bool = False
    trace_notes: list[str] = Field(default_factory=list)
