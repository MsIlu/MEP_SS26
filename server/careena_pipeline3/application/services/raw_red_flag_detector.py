from careena_pipeline3.models.turn.safety_state import (
    SafetyAction,
    SafetyRedFlagStatus,
    SafetyState,
)


class RawRedFlagDetector:
    """Detects raw red-flag signals in the user's original message.

    This detector only produces a SafetyState.
    It does not update the MedicalCase, DialogueState or response text.
    """

    _DYSPNEA_TERMS = (
        "schlecht luft",
        "keine luft",
        "kaum luft",
        "luftnot",
        "atemnot",
        "bekomme keine luft",
        "bekomme schlecht luft",
    )

    _CHEST_PAIN_TERMS = (
        "brustschmerz",
        "brustschmerzen",
        "druck auf der brust",
        "enge in der brust",
    )

    _UNCONSCIOUS_TERMS = (
        "bewusstlos",
        "nicht ansprechbar",
        "ohnmächtig",
    )

    _NOT_BREATHING_TERMS = (
        "atmet nicht",
        "keine atmung",
        "hört auf zu atmen",
    )

    def detect(self, message: str) -> SafetyState:
        """Return raw safety state for the current user message."""

        normalized_message = self._normalize(message)

        confirmed_emergency_terms = self._find_confirmed_emergency_terms(
            normalized_message
        )
        if confirmed_emergency_terms:
            return SafetyState(
                checked_sources=["raw_message"],
                red_flag_detected=True,
                red_flag_status=SafetyRedFlagStatus.CONFIRMED,
                action=SafetyAction.EMERGENCY,
                severity="critical",
                evidence_terms=confirmed_emergency_terms,
                trace_notes=["raw_red_flag:confirmed_emergency"],
            )

        suspected_terms = self._find_suspected_terms(normalized_message)
        if suspected_terms:
            return SafetyState(
                checked_sources=["raw_message"],
                red_flag_detected=True,
                red_flag_status=SafetyRedFlagStatus.SUSPECTED,
                action=SafetyAction.ASK_SAFETY_CLARIFICATION,
                severity="unclear",
                evidence_terms=suspected_terms,
                clarification_question_code="raw_red_flag_clarification",
                trace_notes=["raw_red_flag:suspected_needs_clarification"],
            )

        return SafetyState(
            checked_sources=["raw_message"],
            trace_notes=["raw_red_flag:none"],
        )

    def _find_confirmed_emergency_terms(self, normalized_message: str) -> list[str]:
        """Detect combinations that are enough for immediate emergency handling."""

        unconscious_terms = self._find_terms(
            normalized_message,
            self._UNCONSCIOUS_TERMS,
        )
        not_breathing_terms = self._find_terms(
            normalized_message,
            self._NOT_BREATHING_TERMS,
        )

        if unconscious_terms and not_breathing_terms:
            return unconscious_terms + not_breathing_terms

        return []

    def _find_suspected_terms(self, normalized_message: str) -> list[str]:
        """Detect raw warning signals that need safety clarification."""

        terms = []
        terms.extend(self._find_terms(normalized_message, self._DYSPNEA_TERMS))
        terms.extend(self._find_terms(normalized_message, self._CHEST_PAIN_TERMS))

        return terms

    def _find_terms(self, normalized_message: str, terms: tuple[str, ...]) -> list[str]:
        """Return all configured terms found in the normalized message."""

        return [term for term in terms if term in normalized_message]

    def _normalize(self, message: str) -> str:
        """Normalize user text for simple raw safety matching."""

        return " ".join(message.casefold().strip().split())