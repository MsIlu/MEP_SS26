from careena4.models.turn import SafetyAction, SafetyRedFlagStatus, SafetyState


class RawRedFlagDetector:
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
    _UNCONSCIOUS_TERMS = ("bewusstlos", "nicht ansprechbar", "ohnmaechtig", "ohnmächtig")
    _NOT_BREATHING_TERMS = ("atmet nicht", "keine atmung", "hoert auf zu atmen", "hört auf zu atmen")

    def detect(self, message: str) -> SafetyState:
        normalized_message = self._normalize(message)
        confirmed_emergency_terms = self._find_confirmed_emergency_terms(normalized_message)
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
        unconscious_terms = self._find_terms(normalized_message, self._UNCONSCIOUS_TERMS)
        not_breathing_terms = self._find_terms(normalized_message, self._NOT_BREATHING_TERMS)
        if unconscious_terms and not_breathing_terms:
            return unconscious_terms + not_breathing_terms
        return []

    def _find_suspected_terms(self, normalized_message: str) -> list[str]:
        terms: list[str] = []
        terms.extend(self._find_terms(normalized_message, self._DYSPNEA_TERMS))
        terms.extend(self._find_terms(normalized_message, self._CHEST_PAIN_TERMS))
        return terms

    @staticmethod
    def _find_terms(normalized_message: str, terms: tuple[str, ...]) -> list[str]:
        return [term for term in terms if term in normalized_message]

    @staticmethod
    def _normalize(message: str) -> str:
        normalized = (
            message.casefold()
            .replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ß", "ss")
        )
        return " ".join(normalized.strip().split())
