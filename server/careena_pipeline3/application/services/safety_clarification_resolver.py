from careena_pipeline3.models.domain import PendingSafetyClarification
from careena_pipeline3.models.turn.safety_state import (
    SafetyAction,
    SafetyClarificationOutcome,
    SafetyClarificationResolution,
    SafetyRedFlagStatus,
    SafetyState,
)


class SafetyClarificationResolver:
    """Resolves structured answers to pending safety clarification questions."""

    _CONFIRMS_RED_FLAG = "confirms_red_flag"
    _CLEARS_RED_FLAG = "clears_red_flag"
    _KEEPS_CLARIFICATION_OPEN = "keeps_clarification_open"
    _CONFIRMS_EMERGENCY = "confirms_emergency"

    def resolve(
        self,
        *,
        pending: PendingSafetyClarification,
        answer_code: str,
    ) -> SafetyClarificationResolution:
        """Resolve a structured answer code into a safety resolution."""

        option = self._find_option(pending=pending, answer_code=answer_code)

        if option is None:
            # Unknown structured answers must not be guessed.
            return SafetyClarificationResolution(
                outcome=SafetyClarificationOutcome.INVALID_ANSWER,
                safety_state=SafetyState(
                    checked_sources=["safety_clarification"],
                    red_flag_detected=True,
                    red_flag_status=SafetyRedFlagStatus.SUSPECTED,
                    action=SafetyAction.ASK_SAFETY_CLARIFICATION,
                    evidence_terms=list(pending.evidence_terms),
                    clarification_question_code=pending.question_code,
                    trace_notes=["safety_clarification:invalid_answer"],
                ),
                clear_pending_clarification=False,
                trace_notes=["safety_clarification:invalid_answer"],
            )

        if option.effect_code == self._CONFIRMS_RED_FLAG:
            return SafetyClarificationResolution(
                outcome=SafetyClarificationOutcome.CONFIRMED_RED_FLAG,
                safety_state=SafetyState(
                    checked_sources=["safety_clarification"],
                    red_flag_detected=True,
                    red_flag_status=SafetyRedFlagStatus.CONFIRMED,
                    action=SafetyAction.EMERGENCY,
                    severity="critical",
                    evidence_terms=list(pending.evidence_terms),
                    trace_notes=["safety_clarification:confirmed_red_flag"],
                ),
                clear_pending_clarification=True,
                trace_notes=["safety_clarification:confirmed_red_flag"],
            )

        if option.effect_code == self._CLEARS_RED_FLAG:
            return SafetyClarificationResolution(
                outcome=SafetyClarificationOutcome.CLEARED_RED_FLAG,
                safety_state=SafetyState(
                    checked_sources=["safety_clarification"],
                    red_flag_detected=False,
                    red_flag_status=SafetyRedFlagStatus.CLARIFIED_NEGATIVE,
                    action=SafetyAction.NONE,
                    evidence_terms=list(pending.evidence_terms),
                    trace_notes=["safety_clarification:cleared_red_flag"],
                ),
                clear_pending_clarification=True,
                trace_notes=["safety_clarification:cleared_red_flag"],
            )

        if option.effect_code == self._KEEPS_CLARIFICATION_OPEN:
            return SafetyClarificationResolution(
                outcome=SafetyClarificationOutcome.STILL_UNCLEAR,
                safety_state=SafetyState(
                    checked_sources=["safety_clarification"],
                    red_flag_detected=True,
                    red_flag_status=SafetyRedFlagStatus.SUSPECTED,
                    action=SafetyAction.ASK_SAFETY_CLARIFICATION,
                    severity="unclear",
                    evidence_terms=list(pending.evidence_terms),
                    clarification_question_code=pending.question_code,
                    trace_notes=["safety_clarification:still_unclear"],
                ),
                clear_pending_clarification=False,
                trace_notes=["safety_clarification:still_unclear"],
            )

        if option.effect_code == self._CONFIRMS_EMERGENCY:
            return SafetyClarificationResolution(
                outcome=SafetyClarificationOutcome.CONFIRMED_EMERGENCY,
                safety_state=SafetyState(
                    checked_sources=["safety_clarification"],
                    red_flag_detected=True,
                    red_flag_status=SafetyRedFlagStatus.CONFIRMED,
                    action=SafetyAction.EMERGENCY,
                    severity="critical",
                    evidence_terms=list(pending.evidence_terms),
                    trace_notes=["safety_clarification:confirmed_emergency"],
                ),
                clear_pending_clarification=True,
                trace_notes=["safety_clarification:confirmed_emergency"],
            )

        # Unknown effects are treated as unresolved safety clarification.
        return SafetyClarificationResolution(
            outcome=SafetyClarificationOutcome.INVALID_ANSWER,
            safety_state=SafetyState(
                checked_sources=["safety_clarification"],
                red_flag_detected=True,
                red_flag_status=SafetyRedFlagStatus.SUSPECTED,
                action=SafetyAction.ASK_SAFETY_CLARIFICATION,
                evidence_terms=list(pending.evidence_terms),
                clarification_question_code=pending.question_code,
                trace_notes=["safety_clarification:unknown_effect"],
            ),
            clear_pending_clarification=False,
            trace_notes=["safety_clarification:unknown_effect"],
        )

    def _find_option(
        self,
        *,
        pending: PendingSafetyClarification,
        answer_code: str,
    ):
        """Find the matching guided input option by answer code."""

        normalized_answer_code = answer_code.strip().casefold()

        for option in pending.guided_input.options:
            if option.code.casefold() == normalized_answer_code:
                return option

        return None