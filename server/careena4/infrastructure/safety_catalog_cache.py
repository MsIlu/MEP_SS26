from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from careena4.models.domain import SafetyCatalogMatch

logger = logging.getLogger(__name__)


@dataclass
class _CatalogEntry:
    criterion_key: str
    criterion_label_de: str | None
    description_de: str | None
    lay_terms_normalized: list[str]
    lay_terms_original: list[str]
    urgency_effect: str
    careena_decision_role: str
    criterion_role: str
    is_safety_relevant: bool
    is_red_flag_candidate: bool
    consultation_reason_source_id: str
    consultation_reason_key: str | None
    consultation_reason_label_de: str | None
    source_system: str
    source_version: str | None
    suggested_question_text: str | None
    suggested_input_mode: str
    free_text_allowed: bool


class SafetyCatalogCache:
    """
    In-memory snapshot of all safety-relevant catalog entries.
    Loaded once at server startup to avoid per-turn DB queries.
    """

    def __init__(self) -> None:
        self._entries: list[_CatalogEntry] = []
        self._loaded = False

    def load(self) -> int:
        """Load all active, safety-relevant entries from the DB. Returns entry count."""
        try:
            from database.catalog.models import (
                AssessmentCriterion,
                ConsultationReason,
                ConsultationReasonAssessmentCriterionLink,
            )
            from database.connection import get_db_session
            from sqlmodel import select
        except Exception as exc:
            logger.warning("SafetyCatalogCache could not import DB models: %s", exc)
            return 0

        entries: list[_CatalogEntry] = []
        try:
            with get_db_session() as session:
                links = session.exec(
                    select(ConsultationReasonAssessmentCriterionLink).where(
                        ConsultationReasonAssessmentCriterionLink.is_active == True,
                        ConsultationReasonAssessmentCriterionLink.is_safety_relevant == True,
                        ConsultationReasonAssessmentCriterionLink.is_red_flag_candidate == True,
                    )
                ).all()

                for link in links:
                    reason: ConsultationReason | None = session.get(
                        ConsultationReason, link.consultation_reason_id
                    )
                    criterion: AssessmentCriterion | None = session.get(
                        AssessmentCriterion, link.assessment_criterion_id
                    )
                    if reason is None or criterion is None:
                        continue
                    if not reason.is_active or not criterion.is_active:
                        continue
                    if criterion.careena_capture_status not in {"usable", "conditional"}:
                        continue
                    if criterion.careena_use_policy in {"do_not_ask", "do_not_use"}:
                        continue

                    lay_terms_original = _parse_lang_list(criterion.lay_terms_json, "de")
                    entry = _CatalogEntry(
                        criterion_key=criterion.criterion_key,
                        criterion_label_de=criterion.label_de,
                        description_de=criterion.description_de,
                        lay_terms_original=lay_terms_original,
                        lay_terms_normalized=[_normalize(t) for t in lay_terms_original],
                        urgency_effect=link.urgency_effect or "supporting_context_only",
                        careena_decision_role=link.careena_decision_role or "supporting_context",
                        criterion_role=link.criterion_role or "supporting_criterion",
                        is_safety_relevant=bool(link.is_safety_relevant),
                        is_red_flag_candidate=bool(link.is_red_flag_candidate),
                        consultation_reason_source_id=reason.source_id,
                        consultation_reason_key=reason.careena_key,
                        consultation_reason_label_de=reason.source_label_de,
                        source_system=reason.source_system or "STS",
                        source_version=reason.source_version,
                        suggested_question_text=_first_lang_item(
                            criterion.suggested_question_texts_json, "de"
                        ),
                        suggested_input_mode=criterion.suggested_input_mode or "free_text",
                        free_text_allowed=bool(criterion.free_text_allowed),
                    )
                    entries.append(entry)
        except Exception as exc:
            logger.warning("SafetyCatalogCache load failed: %s", exc)
            return 0

        self._entries = entries
        self._loaded = True
        return len(entries)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def scan_text(self, text: str) -> list[SafetyCatalogMatch]:
        """Match raw user text against all lay_terms in the cache."""
        normalized_text = _normalize(text)
        matches: list[SafetyCatalogMatch] = []
        seen_criteria: set[str] = set()

        for entry in self._entries:
            if entry.criterion_key in seen_criteria:
                continue
            for norm_term, orig_term in zip(
                entry.lay_terms_normalized, entry.lay_terms_original
            ):
                if norm_term and norm_term in normalized_text:
                    if _term_is_negated(normalized_text, norm_term):
                        continue
                    matches.append(_entry_to_match(entry, evidence_term=orig_term, matched_lay_term=orig_term))
                    seen_criteria.add(entry.criterion_key)
                    break

        return matches

    def scan_lay_terms(self, labels: list[str]) -> list[SafetyCatalogMatch]:
        """Match labels against DB lay_terms only. Use for normalized_label_de from extraction."""
        normalized_labels = [_normalize(lbl) for lbl in labels if lbl and lbl.strip()]
        matches: list[SafetyCatalogMatch] = []
        seen_criteria: set[str] = set()

        for entry in self._entries:
            if entry.criterion_key in seen_criteria:
                continue
            for norm_term, orig_term in zip(
                entry.lay_terms_normalized, entry.lay_terms_original
            ):
                if not norm_term:
                    continue
                for norm_label in normalized_labels:
                    if norm_term in norm_label or norm_label in norm_term:
                        matches.append(
                            _entry_to_match(entry, evidence_term=norm_label, matched_lay_term=orig_term)
                        )
                        seen_criteria.add(entry.criterion_key)
                        break
                if entry.criterion_key in seen_criteria:
                    break

        return matches

    def scan_clinical_terms(self, labels: list[str]) -> list[SafetyCatalogMatch]:
        """Match labels against DB criterion_label_de only. Use for clinical_term_de from extraction."""
        normalized_labels = [_normalize(lbl) for lbl in labels if lbl and lbl.strip()]
        matches: list[SafetyCatalogMatch] = []
        seen_criteria: set[str] = set()

        for entry in self._entries:
            if entry.criterion_key in seen_criteria:
                continue
            if not entry.criterion_label_de:
                continue
            norm_crit_label = _normalize(entry.criterion_label_de)
            for norm_label in normalized_labels:
                if norm_label in norm_crit_label or norm_crit_label in norm_label:
                    matches.append(
                        _entry_to_match(
                            entry,
                            evidence_term=norm_label,
                            matched_lay_term=entry.criterion_label_de,
                        )
                    )
                    seen_criteria.add(entry.criterion_key)
                    break

        return matches

    def scan_labels(self, labels: list[str]) -> list[SafetyCatalogMatch]:
        """Match labels against both lay_terms and clinical labels. Used for MedicalCase observations."""
        lay_matches = self.scan_lay_terms(labels)
        seen = {m.criterion_key for m in lay_matches}
        clinical_matches = [
            m for m in self.scan_clinical_terms(labels) if m.criterion_key not in seen
        ]
        return lay_matches + clinical_matches


def _entry_to_match(
    entry: _CatalogEntry, *, evidence_term: str, matched_lay_term: str
) -> SafetyCatalogMatch:
    return SafetyCatalogMatch(
        evidence_term=evidence_term,
        matched_lay_term=matched_lay_term,
        source_system=entry.source_system,
        source_version=entry.source_version,
        consultation_reason_source_id=entry.consultation_reason_source_id,
        consultation_reason_key=entry.consultation_reason_key,
        consultation_reason_label_de=entry.consultation_reason_label_de,
        criterion_key=entry.criterion_key,
        criterion_label_de=entry.criterion_label_de,
        criterion_role=entry.criterion_role,
        urgency_effect=entry.urgency_effect,
        careena_decision_role=entry.careena_decision_role,
        suggested_question_text=entry.suggested_question_text,
        suggested_input_mode=entry.suggested_input_mode,
        free_text_allowed=entry.free_text_allowed,
        is_safety_relevant=entry.is_safety_relevant,
        is_red_flag_candidate=entry.is_red_flag_candidate,
        mapping_status="catalog_matched",
    )


_NEGATION_WORDS = frozenset({
    "kein", "keine", "keinen", "keiner", "keinem", "keines",
    "nicht", "ohne", "weder",
})


def _term_is_negated(normalized_text: str, norm_term: str, window: int = 2) -> bool:
    """Return True when every occurrence of norm_term in normalized_text is preceded by a negation word.

    Works at exact token level. Punctuation is stripped per token so "atemnot," matches "atemnot".
    Conservative: returns True only when ALL occurrences are negated.

    Known limitation: does not handle German morphology (stems/compounds), e.g. "schwindel" in
    "schwindelig" or "schmerzen" in "brustschmerzen". Those cases require LLM-based suppression.
    """
    words = [_strip_punct(w) for w in normalized_text.split()]
    words = [w for w in words if w]
    term_words = norm_term.split()
    n = len(term_words)

    found_any = False
    for i in range(len(words) - n + 1):
        if words[i : i + n] == term_words:
            found_any = True
            pre = words[max(0, i - window) : i]
            if not (set(pre) & _NEGATION_WORDS):
                return False  # at least one non-negated occurrence

    return found_any  # True only when found_any and every occurrence was negated


def _strip_punct(word: str) -> str:
    return "".join(c for c in word if c.isalpha() or c.isdigit())


def _normalize(text: str) -> str:
    return " ".join(
        text.casefold()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
        .split()
    )


def _parse_lang_list(json_str: str | None, lang: str) -> list[str]:
    if not json_str:
        return []
    try:
        data = json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return []
    value = data.get(lang, [])
    if isinstance(value, list):
        return [str(v) for v in value if v]
    if isinstance(value, str) and value:
        return [value]
    return []


def _first_lang_item(json_str: str | None, lang: str) -> str | None:
    items = _parse_lang_list(json_str, lang)
    return items[0].strip() if items else None
