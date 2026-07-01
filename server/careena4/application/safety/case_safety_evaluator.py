from __future__ import annotations

from careena4.models.domain import MedicalCase
from careena4.models.domain.safety_catalog import SafetyCatalogMatch
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus, SafetyState


class CaseSafetyEvaluator:
    """
    Post-extraction safety checks on structured symptom data.

    Three checks in order:
      Check 2 — normalized_label_de from accumulated case observations vs. DB lay_terms
      Check 3 — clinical_term_de from accumulated case observations vs. DB clinical labels
      Check 4 — MedGemma full assessment of accumulated MedicalCase observations

    Check 4 only runs when no DB signal was found (avoids LLM cost on every safe turn).
    All three require a loaded SafetyCatalogCache; missing cache degrades gracefully.
    """

    def __init__(self, catalog_cache=None, llm_client=None) -> None:
        self._catalog_cache = catalog_cache
        self._llm_client = llm_client

    def evaluate(
        self,
        medical_case: MedicalCase,
    ) -> SafetyState:
        cache_ready = self._catalog_cache is not None and self._catalog_cache.is_loaded

        active_observations = [
            obs
            for obs in medical_case.observations
            if obs.type == "symptom" and not obs.is_negated()
        ]

        # Check 2 — lay_terms against accumulated normalized labels
        if cache_ready:
            lay_labels = [
                obs.normalized_label_de
                for obs in active_observations
                if obs.normalized_label_de
            ]
            lay_matches = self._catalog_cache.scan_lay_terms(lay_labels) if lay_labels else []
            safety_lay = [m for m in lay_matches if _is_safety_relevant(m)]
            if safety_lay:
                return self._suspected_state(
                    matches=safety_lay,
                    sources=["medical_case_observations", "catalog_lay_terms"],
                    check_tag="check2_lay_terms",
                )

        # Check 3 — clinical labels against accumulated clinical terms
        if cache_ready:
            clinical_labels = [
                obs.clinical_term_de
                for obs in active_observations
                if obs.clinical_term_de
            ]
            clinical_matches = self._catalog_cache.scan_clinical_terms(clinical_labels) if clinical_labels else []
            safety_clinical = [m for m in clinical_matches if _is_safety_relevant(m)]
            if safety_clinical:
                return self._suspected_state(
                    matches=safety_clinical,
                    sources=["medical_case_observations", "catalog_clinical_terms"],
                    check_tag="check3_clinical_terms",
                )

        # Check 4 — MedGemma full assessment on accumulated MedicalCase
        active_labels = [obs.normalized_label_de for obs in active_observations]
        if active_labels and self._llm_client is not None:
            if _ask_medgemma_safety(self._llm_client, active_labels):
                return self._suspected_state(
                    matches=[],
                    sources=["medical_case_observations", "medgemma_assessment"],
                    check_tag="check4_medgemma",
                )

        return SafetyState(
            checked_sources=["medical_case_observations"],
            trace_notes=["case_safety:none"],
        )

    @staticmethod
    def _suspected_state(
        *,
        matches: list[SafetyCatalogMatch],
        sources: list[str],
        check_tag: str,
    ) -> SafetyState:
        evidence = list({m.matched_lay_term or m.evidence_term for m in matches}) if matches else []
        trace = [f"case_safety:{check_tag}"]
        if matches:
            trace += [f"case_safety:catalog_match:{m.criterion_key}" for m in matches[:3]]
        return SafetyState(
            checked_sources=sources,
            red_flag_detected=True,
            red_flag_status=SafetyRedFlagStatus.SUSPECTED,
            action=SafetyAction.ASK_SAFETY_CLARIFICATION,
            severity="unclear",
            evidence_terms=evidence,
            clarification_question_code="case_safety_clarification",
            trace_notes=["case_safety:suspected", *trace],
        )


def _is_safety_relevant(match: SafetyCatalogMatch) -> bool:
    return match.urgency_effect in {
        "requires_safety_clarification",
        "confirms_emergency",
        "blocks_deescalation",
    }


def _ask_medgemma_safety(llm_client, labels: list[str]) -> bool:
    symptom_list = ", ".join(labels)
    prompt = (
        f"Ein Patient berichtet folgende Symptome: {symptom_list}.\n"
        "Könnte diese Kombination auf einen medizinischen Notfall oder eine dringende "
        "medizinische Situation hinweisen?\n"
        "Antworte nur mit JA oder NEIN."
    )
    try:
        response = llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0.0,
        )
        answer = (response or "").strip().upper()
        return answer.startswith("JA") or answer.startswith("YES")
    except Exception:
        return False
