from __future__ import annotations

from careena4.models.safety import CurrentTurnSafetyEvidence, StructuredSafetyResult
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus


class StructuredRedFlagEvaluator:
    """
    Evaluate structured current-turn evidence for red-flag signals.

    This evaluator is deterministic and rule-based. It does not call an LLM, does
    not update MedicalCase and does not generate frontend responses. It uses
    internal text signal groups only; external medical code systems must not
    decide safety in this layer.
    """

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
        "blaue lippen",
        "lippen blau",
        "zyanose",
        "cyanose",
        "sprechdyspnoe",
        "respiratorische erschoepfung",
        "respiratorische ersch?pfung",
    )

    _SUSPECTED_DYSPNEA_TERMS = (
        "atemnot",
        "dyspnoe",
        "luftnot",
        "schlecht luft",
        "bekomme schlecht luft",
        "kaum luft",
    )

    _CHEST_PAIN_TERMS = (
        "brustschmerz",
        "brustschmerzen",
        "druck auf der brust",
        "enge in der brust",
        "thoraxschmerz",
        "thoraxschmerzen",
    )

    def evaluate(
        self,
        evidence: CurrentTurnSafetyEvidence,
    ) -> StructuredSafetyResult:
        """
        Return structured safety result for the current turn only.
        """

        searchable_text = evidence.searchable_text()

        critical_terms = self._find_terms(
            searchable_text,
            self._CRITICAL_DYSPNEA_TERMS,
        )
        if critical_terms:
            return StructuredSafetyResult(
                red_flag_status=SafetyRedFlagStatus.CONFIRMED,
                action=SafetyAction.EMERGENCY,
                severity="critical",
                matched_terms=critical_terms,
                matched_snomed_codes=[],
                matched_rule_ids=["structured_critical_dyspnea"],
                consultation_reason_source_ids=["1008"],
                trace_notes=["structured_red_flag:confirmed_critical_dyspnea"],
            )

        suspected_terms: list[str] = []
        consultation_reason_source_ids: list[str] = []
        matched_rule_ids: list[str] = []

        dyspnea_terms = self._find_terms(searchable_text, self._SUSPECTED_DYSPNEA_TERMS)
        if dyspnea_terms:
            suspected_terms.extend(dyspnea_terms)
            consultation_reason_source_ids.append("1008")
            matched_rule_ids.append("structured_suspected_dyspnea")

        chest_pain_terms = self._find_terms(searchable_text, self._CHEST_PAIN_TERMS)
        if chest_pain_terms:
            suspected_terms.extend(chest_pain_terms)
            consultation_reason_source_ids.append("1002")
            matched_rule_ids.append("structured_suspected_chest_pain")

        suspected_terms = self._deduplicate(suspected_terms)
        consultation_reason_source_ids = self._deduplicate(consultation_reason_source_ids)
        matched_rule_ids = self._deduplicate(matched_rule_ids)

        if matched_rule_ids:
            return StructuredSafetyResult(
                red_flag_status=SafetyRedFlagStatus.SUSPECTED,
                action=SafetyAction.ASK_SAFETY_CLARIFICATION,
                severity="unclear",
                matched_terms=suspected_terms,
                matched_snomed_codes=[],
                matched_rule_ids=matched_rule_ids,
                consultation_reason_source_ids=consultation_reason_source_ids,
                clarification_question_code="structured_red_flag_clarification",
                trace_notes=["structured_red_flag:suspected_needs_clarification"],
            )

        return StructuredSafetyResult(
            trace_notes=["structured_red_flag:none"],
        )

    @staticmethod
    def _find_terms(searchable_text: str, terms: tuple[str, ...]) -> list[str]:
        """
        Return configured terms found in normalized current evidence.
        """

        return [term for term in terms if _normalize(term) in searchable_text]

    @staticmethod
    def _deduplicate(values: list[str]) -> list[str]:
        """
        Return values without duplicates while preserving order.
        """

        result: list[str] = []
        for value in values:
            if value not in result:
                result.append(value)
        return result


def _normalize(text: str) -> str:
    """
    Normalize German lay and mojibake variants for deterministic matching.
    """

    normalized = (
        text.casefold()
        .replace("?", "ae")
        .replace("?", "oe")
        .replace("?", "ue")
        .replace("?", "ss")
        .replace("??", "ae")
        .replace("??", "oe")
        .replace("??", "ue")
        .replace("??", "ss")
    )
    return " ".join(normalized.split())