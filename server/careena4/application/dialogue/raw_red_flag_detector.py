"""Raw current-message red-flag detection for Careena4.

This module is the deterministic safety airbag before LLM-based extraction. It
only reads the current raw message and returns a SafetyState. It must not update
MedicalCase, ConversationState, recommendations or response text.
"""

from careena4.models.turn import SafetyAction, SafetyRedFlagStatus, SafetyState


class RawRedFlagDetector:
    """Detect raw safety signals in the user's current message only."""

    _CRITICAL_DYSPNEA_TERMS = (
        "bekomme keine luft",
        "bekomm keine luft",
        "kriege keine luft",
        "krieg keine luft",
        "keine luft mehr",
        "keine luft",
        "kann nicht atmen",
        "bekomme keinen atem",
        "ersticke",
    )

    _DYSPNEA_TERMS = (
        "schlecht luft",
        "bekomme schlecht luft",
        "kaum luft",
        "luftnot",
        "atemnot",
        "dyspnoe",
    )

    _NEGATED_DYSPNEA_TERMS = (
        "keine atemnot",
        "keine luftnot",
        "keine dyspnoe",
        "nicht kurzatmig",
        "bekomme normal luft",
        "bekomme gut luft",
        "ich atme normal",
        "atme normal",
    )

    _CHEST_PAIN_TERMS = (
        "brustschmerz",
        "brustschmerzen",
        "druck auf der brust",
        "enge in der brust",
        "thoraxschmerz",
        "thoraxschmerzen",
    )

    _NEGATED_CHEST_PAIN_TERMS = (
        "keine brustschmerzen",
        "keinen brustschmerz",
        "kein brustschmerz",
        "kein druck auf der brust",
        "keine enge in der brust",
        "keine thoraxschmerzen",
    )

    _UNCONSCIOUS_TERMS = (
        "bewusstlos",
        "nicht ansprechbar",
        "ohnmaechtig",
        "nicht wach zu bekommen",
        "reagiert nicht",
    )

    _NOT_BREATHING_TERMS = (
        "atmet nicht",
        "keine atmung",
        "hoert auf zu atmen",
        "atmet gar nicht",
    )

    _ACUTE_NEUROLOGIC_TERMS = (
        "laehmung",
        "gelaehmt",
        "halbseitig",
        "mundwinkel haengt",
        "haengender mundwinkel",
        "gesicht haengt",
        "sprachstoerung",
        "verwaschene sprache",
        "arm schwach",
        "bein schwach",
    )

    _NEGATED_NEUROLOGIC_TERMS = (
        "keine laehmung",
        "nicht gelaehmt",
        "kein haengender mundwinkel",
        "keine sprachstoerung",
    )

    _ALTERED_CONSCIOUSNESS_TERMS = (
        "kaum wach",
        "schwer wach zu bekommen",
        "nicht richtig wach",
        "reagiert kaum",
        "nur kurz ansprechbar",
        "sehr verwirrt",
        "extrem benommen",
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
        """Return raw terms that are strong enough for immediate emergency handling."""

        critical_dyspnea_terms = self._find_terms(
            normalized_message,
            self._CRITICAL_DYSPNEA_TERMS,
        )
        if critical_dyspnea_terms and not self._contains_any(
            normalized_message,
            self._NEGATED_DYSPNEA_TERMS,
        ):
            return self._deduplicate(critical_dyspnea_terms)

        unconscious_terms = self._find_terms(normalized_message, self._UNCONSCIOUS_TERMS)
        not_breathing_terms = self._find_terms(
            normalized_message,
            self._NOT_BREATHING_TERMS,
        )
        if unconscious_terms and not_breathing_terms:
            return self._deduplicate(unconscious_terms + not_breathing_terms)

        return []

    def _find_suspected_terms(self, normalized_message: str) -> list[str]:
        """Return suspected raw red-flag terms after simple negation guards."""

        terms: list[str] = []

        if not self._contains_any(normalized_message, self._NEGATED_DYSPNEA_TERMS):
            terms.extend(self._find_terms(normalized_message, self._DYSPNEA_TERMS))

        if not self._contains_any(normalized_message, self._NEGATED_CHEST_PAIN_TERMS):
            terms.extend(self._find_terms(normalized_message, self._CHEST_PAIN_TERMS))

        if not self._contains_any(normalized_message, self._NEGATED_NEUROLOGIC_TERMS):
            terms.extend(self._find_terms(normalized_message, self._ACUTE_NEUROLOGIC_TERMS))

        terms.extend(self._find_terms(normalized_message, self._ALTERED_CONSCIOUSNESS_TERMS))

        return self._deduplicate(terms)

    @classmethod
    def _contains_any(cls, normalized_message: str, terms: tuple[str, ...]) -> bool:
        """Return True if any normalized guard term is present."""

        return any(cls._normalize(term) in normalized_message for term in terms)

    @classmethod
    def _find_terms(cls, normalized_message: str, terms: tuple[str, ...]) -> list[str]:
        """Return configured normalized terms found in the current message."""

        return [
            cls._normalize(term)
            for term in terms
            if cls._normalize(term) in normalized_message
        ]

    @staticmethod
    def _deduplicate(values: list[str]) -> list[str]:
        """Return values without duplicates while preserving order."""

        result: list[str] = []
        for value in values:
            if value not in result:
                result.append(value)
        return result

    @staticmethod
    def _normalize(message: str) -> str:
        """Normalize German umlauts and common mojibake variants."""

        normalized = (
            message.casefold()
            .replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ß", "ss")
            .replace("ã¤", "ae")
            .replace("ã¶", "oe")
            .replace("ã¼", "ue")
            .replace("ãÿ", "ss")
            .replace("Ã¤", "ae")
            .replace("Ã¶", "oe")
            .replace("Ã¼", "ue")
            .replace("ÃŸ", "ss")
        )
        return " ".join(normalized.strip().split())
