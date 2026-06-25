from __future__ import annotations

from careena4.models.domain import SafetyCatalogMatch
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus, SafetyState

# Minimal hardcoded patterns for unambiguous life-threatening combinations only.
# Everything else is detected via the SafetyCatalogCache (DB lay_terms).
_UNCONSCIOUS_TERMS = (
    "bewusstlos",
    "nicht ansprechbar",
    "ohnmaechtig",
    "ohnmächtig",
)
_NOT_BREATHING_TERMS = (
    "atmet nicht",
    "keine atmung",
    "hoert auf zu atmen",
    "hört auf zu atmen",
    "keine luft mehr",
    "bekommt keine luft",
    "bekomme keine luft",
)


class RawRedFlagDetector:
    """
    Fast deterministic safety check on raw message text.

    CONFIRMED: only for unambiguous life-threatening combinations (e.g. unconscious
    AND not breathing). Stays hardcoded because DB cannot express AND-combinations.

    SUSPECTED: any safety-relevant lay_term found in text via SafetyCatalogCache.
    Falls back gracefully when no cache is available.
    """

    def __init__(self, catalog_cache=None) -> None:
        self._catalog_cache = catalog_cache

    def detect(self, message: str) -> SafetyState:
        normalized = _normalize(message)

        # CONFIRMED — extreme life-threatening combination (hardcoded, minimal)
        unconscious = _find_terms(normalized, _UNCONSCIOUS_TERMS)
        not_breathing = _find_terms(normalized, _NOT_BREATHING_TERMS)
        if unconscious and not_breathing:
            return SafetyState(
                checked_sources=["raw_message"],
                red_flag_detected=True,
                red_flag_status=SafetyRedFlagStatus.CONFIRMED,
                action=SafetyAction.ASK_SAFETY_CLARIFICATION,
                severity="critical",
                evidence_terms=unconscious + not_breathing,
                clarification_question_code="raw_red_flag_clarification",
                trace_notes=["raw_red_flag:confirmed_critical"],
            )

        # SUSPECTED — DB lay_terms match
        if self._catalog_cache is not None and self._catalog_cache.is_loaded:
            matches: list[SafetyCatalogMatch] = self._catalog_cache.scan_text(message)
            safety_matches = [
                m for m in matches
                if m.urgency_effect in {
                    "requires_safety_clarification",
                    "confirms_emergency",
                    "blocks_deescalation",
                }
            ]
            if safety_matches:
                evidence_terms = list({m.matched_lay_term or m.evidence_term for m in safety_matches})
                return SafetyState(
                    checked_sources=["raw_message", "catalog_lay_terms"],
                    red_flag_detected=True,
                    red_flag_status=SafetyRedFlagStatus.SUSPECTED,
                    action=SafetyAction.ASK_SAFETY_CLARIFICATION,
                    severity="unclear",
                    evidence_terms=evidence_terms,
                    clarification_question_code="raw_red_flag_clarification",
                    trace_notes=[
                        "raw_red_flag:suspected_catalog_match",
                        *[f"raw_red_flag:matched:{m.criterion_key}" for m in safety_matches[:3]],
                    ],
                )

        return SafetyState(
            checked_sources=["raw_message"],
            trace_notes=["raw_red_flag:none"],
        )


def _normalize(text: str) -> str:
    return " ".join(
        text.casefold()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
        .split()
    )


def _find_terms(normalized_text: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if _normalize(term) in normalized_text]
