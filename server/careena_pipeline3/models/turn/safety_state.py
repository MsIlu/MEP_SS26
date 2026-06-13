from enum import Enum

from pydantic import Field

from careena_pipeline3.models.common import PipelineModel


class SafetyRedFlagStatus(str, Enum):
    """Lifecycle state of a red-flag signal."""

    NONE = "none"
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    CLARIFIED_NEGATIVE = "clarified_negative"
    RESOLVED = "resolved"


class SafetyAction(str, Enum):
    """Next safety-related action requested by the pipeline."""

    NONE = "none"
    ASK_SAFETY_CLARIFICATION = "ask_safety_clarification"
    EMERGENCY = "emergency"


class SafetyClarificationOutcome(str, Enum):
    """Result of resolving a structured safety clarification answer."""

    CONFIRMED_RED_FLAG = "confirmed_red_flag"
    CLEARED_RED_FLAG = "cleared_red_flag"
    STILL_UNCLEAR = "still_unclear"
    CONFIRMED_EMERGENCY = "confirmed_emergency"
    INVALID_ANSWER = "invalid_answer"

class SafetyState(PipelineModel):
    """Safety result for one pipeline turn.

    This model stores safety state only.
    It does not detect red flags and does not generate responses.
    """

    checked_sources: list[str] = Field(default_factory=list)
    """Sources checked during this safety stage, e.g. raw text, extraction or case."""

    red_flag_detected: bool = False
    """Legacy flag kept for compatibility.

    New logic should prefer red_flag_status and action.
    A detected red-flag signal is not automatically a confirmed emergency.
    """

    red_flag_status: SafetyRedFlagStatus = SafetyRedFlagStatus.NONE
    """Current state of the red-flag signal."""

    action: SafetyAction = SafetyAction.NONE
    """Requested safety action for the next pipeline step."""

    severity: str | None = None
    """Optional severity label; will be refined with STS-based safety logic."""

    evidence_terms: list[str] = Field(default_factory=list)
    """Terms or phrases that triggered this safety state."""

    clarification_question_code: str | None = None
    """Code for a targeted safety clarification question."""

    trace_notes: list[str] = Field(default_factory=list)
    """Internal notes for debugging and traceability."""

    @property
    def requires_emergency_response(self) -> bool:
        """Return True only for confirmed emergency handling."""

        return (
            self.red_flag_status == SafetyRedFlagStatus.CONFIRMED
            or self.action == SafetyAction.EMERGENCY
        )

    @property
    def requires_safety_clarification(self) -> bool:
        """Return True when a suspected red flag needs clarification."""

        return (
            self.red_flag_status == SafetyRedFlagStatus.SUSPECTED
            and self.action == SafetyAction.ASK_SAFETY_CLARIFICATION
        )
        
class SafetyClarificationResolution(PipelineModel):
    """Resolution result for one structured safety clarification answer."""

    outcome: SafetyClarificationOutcome
    safety_state: SafetyState
    clear_pending_clarification: bool = False
    trace_notes: list[str] = Field(default_factory=list)
