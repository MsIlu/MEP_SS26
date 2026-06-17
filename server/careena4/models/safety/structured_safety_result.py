from __future__ import annotations

from pydantic import Field

from careena4.models.common import PipelineModel
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus, SafetyState


class StructuredSafetyResult(PipelineModel):
    """
    Result of structured red-flag evaluation for the current turn.

    This is not a frontend response and not a recommendation. It is an internal
    safety signal that can later be merged with raw safety by a safety arbitrator.
    """

    checked_sources: list[str] = Field(default_factory=lambda: ["current_turn_evidence"])
    red_flag_status: SafetyRedFlagStatus = SafetyRedFlagStatus.NONE
    action: SafetyAction = SafetyAction.NONE
    severity: str | None = None
    matched_terms: list[str] = Field(default_factory=list)
    matched_snomed_codes: list[str] = Field(default_factory=list)
    matched_rule_ids: list[str] = Field(default_factory=list)
    consultation_reason_source_ids: list[str] = Field(default_factory=list)
    clarification_question_code: str | None = None
    trace_notes: list[str] = Field(default_factory=list)

    @property
    def red_flag_detected(self) -> bool:
        """
        Return True when structured safety found any red-flag signal.
        """

        return self.red_flag_status != SafetyRedFlagStatus.NONE

    @property
    def requires_emergency_response(self) -> bool:
        """
        Return True only for confirmed structured emergency handling.
        """

        return (
            self.red_flag_status == SafetyRedFlagStatus.CONFIRMED
            or self.action == SafetyAction.EMERGENCY
        )

    @property
    def requires_safety_clarification(self) -> bool:
        """
        Return True when structured evidence needs safety clarification.
        """

        return (
            self.red_flag_status == SafetyRedFlagStatus.SUSPECTED
            and self.action == SafetyAction.ASK_SAFETY_CLARIFICATION
        )

    def to_safety_state(self) -> SafetyState:
        """
        Convert this result to the existing SafetyState contract.
        """

        return SafetyState(
            checked_sources=list(self.checked_sources),
            red_flag_detected=self.red_flag_detected,
            red_flag_status=self.red_flag_status,
            action=self.action,
            severity=self.severity,
            evidence_terms=list(self.matched_terms),
            clarification_question_code=self.clarification_question_code,
            trace_notes=list(self.trace_notes),
        )
