from careena4.models.domain import ActiveQuestion
from careena4.models.turn import (
    SafetyAction,
    SafetyClarificationOutcome,
    SafetyClarificationResolution,
    SafetyRedFlagStatus,
    SafetyState,
)


class SafetyClarificationResolver:
    _CONFIRMS_RED_FLAG = "confirms_red_flag"
    _CLEARS_RED_FLAG = "clears_red_flag"
    _KEEPS_CLARIFICATION_OPEN = "keeps_clarification_open"
    _CONFIRMS_EMERGENCY = "confirms_emergency"

    def resolve(self, *, question: ActiveQuestion, answer_code: str) -> SafetyClarificationResolution:
        option = self._find_option(question=question, answer_code=answer_code)
        if option is None:
            return SafetyClarificationResolution(
                outcome=SafetyClarificationOutcome.INVALID_ANSWER,
                safety_state=SafetyState(
                    checked_sources=["safety_clarification"],
                    red_flag_detected=True,
                    red_flag_status=SafetyRedFlagStatus.SUSPECTED,
                    action=SafetyAction.ASK_SAFETY_CLARIFICATION,
                    evidence_terms=self._evidence_terms(question),
                    clarification_question_code=self._question_code(question),
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
                    evidence_terms=self._evidence_terms(question),
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
                    evidence_terms=self._evidence_terms(question),
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
                    evidence_terms=self._evidence_terms(question),
                    clarification_question_code=self._question_code(question),
                    trace_notes=["safety_clarification:still_unclear"],
                ),
                clear_pending_clarification=False,
                trace_notes=["safety_clarification:still_unclear"],
            )
        return SafetyClarificationResolution(
            outcome=SafetyClarificationOutcome.CONFIRMED_EMERGENCY,
            safety_state=SafetyState(
                checked_sources=["safety_clarification"],
                red_flag_detected=True,
                red_flag_status=SafetyRedFlagStatus.CONFIRMED,
                action=SafetyAction.EMERGENCY,
                severity="critical",
                evidence_terms=self._evidence_terms(question),
                trace_notes=["safety_clarification:confirmed_emergency"],
            ),
            clear_pending_clarification=True,
            trace_notes=["safety_clarification:confirmed_emergency"],
        )

    @staticmethod
    def _evidence_terms(question: ActiveQuestion) -> list[str]:
        """Read safety evidence from the new context, with legacy fallback."""

        if question.safety_context is not None:
            return list(question.safety_context.evidence_terms)
        return list(question.safety_evidence_terms)

    @staticmethod
    def _question_code(question: ActiveQuestion) -> str | None:
        """Read the safety question code from the new context, with legacy fallback."""

        if question.safety_context is not None:
            return question.safety_context.question_code
        return question.safety_question_code

    @staticmethod
    def _find_option(*, question: ActiveQuestion, answer_code: str):
        if question.guided_input is None:
            return None
        normalized_answer_code = answer_code.strip().casefold()
        for option in question.guided_input.options:
            if option.code.casefold() == normalized_answer_code:
                return option
            if option.label.strip().casefold() == normalized_answer_code:
                return option
        return None

