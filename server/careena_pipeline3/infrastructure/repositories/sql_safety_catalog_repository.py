import json
from collections.abc import Callable
from typing import Any

from sqlmodel import Session, select

from careena_pipeline3.models.domain import SafetyCatalogMatch
from database.catalog.models import (
    AssessmentCriterion,
    ConsultationReason,
    ConsultationReasonAssessmentCriterionLink,
)
from database.connection import get_db_session


class SqlSafetyCatalogRepository:
    """SQL-backed repository for safety-relevant catalog criteria."""

    def __init__(
        self,
        session_factory: Callable[[], Session] = get_db_session,
        language: str = "de",
    ):
        self.session_factory = session_factory
        self.language = language

    def find_matches_for_evidence_terms(
        self,
        evidence_terms: list[str],
    ) -> list[SafetyCatalogMatch]:
        """Find safety-relevant catalog matches for raw safety evidence."""

        normalized_evidence_terms = [
            self._normalize(term) for term in evidence_terms if term.strip()
        ]

        if not normalized_evidence_terms:
            return []

        matches: list[SafetyCatalogMatch] = []

        with self.session_factory() as session:
            links = session.exec(
                select(ConsultationReasonAssessmentCriterionLink).where(
                    ConsultationReasonAssessmentCriterionLink.is_active == True,
                    ConsultationReasonAssessmentCriterionLink.is_safety_relevant == True,
                    ConsultationReasonAssessmentCriterionLink.is_red_flag_candidate == True,
                )
            ).all()

            for link in links:
                reason = session.get(ConsultationReason, link.consultation_reason_id)
                criterion = session.get(
                    AssessmentCriterion,
                    link.assessment_criterion_id,
                )

                if reason is None or criterion is None:
                    continue

                if not self._is_runtime_usable(reason, criterion):
                    continue

                lay_terms = self._language_list(criterion.lay_terms_json)
                matched = self._find_lay_term_match(
                    normalized_evidence_terms,
                    lay_terms,
                )

                if matched is None:
                    continue

                evidence_term, matched_lay_term = matched

                matches.append(
                    SafetyCatalogMatch(
                        evidence_term=evidence_term,
                        matched_lay_term=matched_lay_term,
                        source_system=reason.source_system,
                        source_version=reason.source_version,
                        consultation_reason_source_id=reason.source_id,
                        consultation_reason_key=reason.careena_key,
                        consultation_reason_label_de=reason.source_label_de,
                        criterion_key=criterion.criterion_key,
                        criterion_label_de=criterion.label_de,
                        criterion_role=link.criterion_role,
                        urgency_effect=link.urgency_effect,
                        careena_decision_role=link.careena_decision_role,
                        suggested_question_text=self._first_question(
                            criterion.suggested_question_texts_json
                        ),
                        suggested_input_mode=criterion.suggested_input_mode,
                        free_text_allowed=criterion.free_text_allowed,
                        is_safety_relevant=link.is_safety_relevant,
                        is_red_flag_candidate=link.is_red_flag_candidate,
                        mapping_status="catalog_matched",
                        trace_notes=[
                            f"consultation_reason_id={reason.id}",
                            f"assessment_criterion_id={criterion.id}",
                            f"link_id={link.id}",
                        ],
                    )
                )

        return matches

    def _is_runtime_usable(
        self,
        reason: ConsultationReason,
        criterion: AssessmentCriterion,
    ) -> bool:
        """Return whether catalog data may be used by runtime safety lookup."""

        if not reason.is_active or not criterion.is_active:
            return False

        if criterion.careena_capture_status not in {"usable", "conditional"}:
            return False

        if criterion.careena_use_policy in {"do_not_ask", "do_not_use"}:
            return False

        return True

    def _find_lay_term_match(
        self,
        normalized_evidence_terms: list[str],
        lay_terms: list[str],
    ) -> tuple[str, str] | None:
        """Match raw evidence terms against catalog lay terms."""

        normalized_lay_terms = [
            self._normalize(term) for term in lay_terms if term.strip()
        ]

        for evidence_term in normalized_evidence_terms:
            for lay_term in normalized_lay_terms:
                if evidence_term == lay_term:
                    return evidence_term, lay_term
                if evidence_term in lay_term:
                    return evidence_term, lay_term
                if lay_term in evidence_term:
                    return evidence_term, lay_term

        return None

    def _first_question(self, value: str) -> str | None:
        """Return the first non-empty suggested question for the configured language."""

        questions = self._language_list(value)

        for question in questions:
            cleaned = question.strip()
            if cleaned:
                return cleaned

        return None

    def _language_list(self, value: str) -> list[str]:
        """Parse a JSON language map and return values for the configured language."""

        parsed = self._load_json_dict(value)
        language_value = parsed.get(self.language)

        if isinstance(language_value, list):
            return [str(item) for item in language_value]

        if isinstance(language_value, str):
            return [language_value]

        return []

    @staticmethod
    def _load_json_dict(value: str) -> dict[str, Any]:
        """Parse JSON object fields stored as strings in the catalog tables."""

        try:
            parsed = json.loads(value or "{}")
        except json.JSONDecodeError:
            return {}

        if isinstance(parsed, dict):
            return parsed

        return {}

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize user-facing terms for predictable catalog matching."""

        return " ".join(value.casefold().strip().split())