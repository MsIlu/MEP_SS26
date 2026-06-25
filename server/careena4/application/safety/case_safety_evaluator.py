from __future__ import annotations

from careena4.models.domain import MedicalCase
from careena4.models.domain.safety_catalog import SafetyCatalogMatch
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus, SafetyState


class CaseSafetyEvaluator:
    """
    Post-extraction safety check that operates on all active observations in the
    MedicalCase — not just the current turn's raw text.

    Checks extracted symptom labels against:
      a) DB lay_terms (via SafetyCatalogCache)
      b) DB clinical labels (criterion_label_de, also via cache)
      c) Optionally MedGemma for combination risk assessment

    This catches safety-relevant symptom combinations that build up across
    multiple turns and would be missed by the per-turn raw check.
    """

    def __init__(self, catalog_cache=None, llm_client=None) -> None:
        self._catalog_cache = catalog_cache
        self._llm_client = llm_client

    def evaluate(self, medical_case: MedicalCase) -> SafetyState:
        active_labels = self._active_labels(medical_case)
        if not active_labels:
            return SafetyState(
                checked_sources=["case_observations"],
                trace_notes=["case_safety:no_active_observations"],
            )

        catalog_matches = self._catalog_matches(active_labels)
        medgemma_signal = self._medgemma_check(active_labels, catalog_matches)

        if not catalog_matches and not medgemma_signal:
            return SafetyState(
                checked_sources=["case_observations", "catalog_labels"],
                trace_notes=["case_safety:none"],
            )

        # Consensus: either DB or MedGemma found something → red flag wins
        all_evidence = list({m.matched_lay_term or m.evidence_term for m in catalog_matches})
        sources = ["case_observations", "catalog_labels"]
        trace = []

        if catalog_matches:
            trace += [f"case_safety:catalog_match:{m.criterion_key}" for m in catalog_matches[:3]]
        if medgemma_signal:
            sources.append("medgemma_assessment")
            trace.append("case_safety:medgemma_confirmed")

        return SafetyState(
            checked_sources=sources,
            red_flag_detected=True,
            red_flag_status=SafetyRedFlagStatus.SUSPECTED,
            action=SafetyAction.ASK_SAFETY_CLARIFICATION,
            severity="unclear",
            evidence_terms=all_evidence,
            clarification_question_code="case_safety_clarification",
            trace_notes=["case_safety:suspected", *trace],
        )

    def _active_labels(self, medical_case: MedicalCase) -> list[str]:
        labels = []
        for obs in medical_case.observations:
            if not obs.is_negated():
                labels.append(obs.label)
        return labels

    def _catalog_matches(self, labels: list[str]) -> list[SafetyCatalogMatch]:
        if self._catalog_cache is None or not self._catalog_cache.is_loaded:
            return []
        return self._catalog_cache.scan_labels(labels)

    def _medgemma_check(
        self,
        labels: list[str],
        catalog_matches: list[SafetyCatalogMatch],
    ) -> bool:
        if self._llm_client is None or not labels:
            return False
        # Only call MedGemma when there's already a catalog signal —
        # avoids LLM call overhead on every safe turn.
        if not catalog_matches:
            return False
        try:
            return _ask_medgemma_safety(self._llm_client, labels)
        except Exception:
            return False



def _ask_medgemma_safety(llm_client, labels: list[str]) -> bool:
    """
    Ask MedGemma whether the symptom combination is potentially dangerous.
    Returns True if MedGemma considers it a medical concern.
    """
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
