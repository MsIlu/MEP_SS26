import logging

from careena_pipeline3.application.repositories import SafetyCatalogRepository
from careena_pipeline3.models.domain import PendingSafetyClarification, SafetyCatalogMatch
from careena_pipeline3.models.turn import SafetyState


logger = logging.getLogger(__name__)


class SafetyClarificationBuilder:
    """Builds pending safety clarifications from catalog-backed safety matches."""

    def __init__(
        self,
        safety_catalog_repository: SafetyCatalogRepository | None = None,
    ):
        self.safety_catalog_repository = safety_catalog_repository

    def build_pending_clarification(
        self,
        *,
        safety_state: SafetyState,
        source_stage: str,
    ) -> PendingSafetyClarification:
        """Build a pending safety clarification from safety evidence and catalog data."""

        question_code = (
            safety_state.clarification_question_code
            or "raw_red_flag_clarification"
        )
        evidence_terms = list(safety_state.evidence_terms)

        if self.safety_catalog_repository is None or not evidence_terms:
            return PendingSafetyClarification(
                question_code=question_code,
                source_stage=source_stage,
                source_system="STS",
                evidence_terms=evidence_terms,
            )

        try:
            match = self._find_best_catalog_match(evidence_terms)
        except Exception:
            logger.exception(
                "Safety catalog lookup failed; using generic safety clarification fallback."
            )
            return PendingSafetyClarification(
                question_code=question_code,
                source_stage=source_stage,
                source_system="STS",
                catalog_mapping_status="fallback_catalog_unavailable",
                evidence_terms=evidence_terms,
            )

        if match is not None:
            return PendingSafetyClarification(
                question_code=question_code,
                source_stage=source_stage,
                question_text=match.suggested_question_text,
                source_system=match.source_system,
                source_version=match.source_version,
                consultation_reason_source_id=match.consultation_reason_source_id,
                consultation_reason_key=match.consultation_reason_key,
                criterion_key=match.criterion_key,
                criterion_role=match.criterion_role,
                urgency_effect=match.urgency_effect,
                catalog_mapping_status=match.mapping_status,
                evidence_terms=evidence_terms,
            )

        return PendingSafetyClarification(
            question_code=question_code,
            source_stage=source_stage,
            source_system="STS",
            catalog_mapping_status="fallback_no_catalog_match",
            evidence_terms=evidence_terms,
        )

    def _find_best_catalog_match(
        self,
        evidence_terms: list[str],
    ) -> SafetyCatalogMatch | None:
        """Find the best generic catalog match for a safety clarification."""

        if self.safety_catalog_repository is None or not evidence_terms:
            return None

        matches = self.safety_catalog_repository.find_matches_for_evidence_terms(
            evidence_terms
        )

        clarification_matches = [
            match
            for match in matches
            if match.urgency_effect == "requires_safety_clarification"
            and match.suggested_question_text
            and match.is_safety_relevant
            and match.is_red_flag_candidate
        ]

        if not clarification_matches:
            return None

        return max(clarification_matches, key=self._match_priority)

    @staticmethod
    def _match_priority(match: SafetyCatalogMatch) -> int:
        """Score matches by generic safety metadata, never by symptom identity."""

        score = 0

        if match.is_safety_relevant:
            score += 20

        if match.is_red_flag_candidate:
            score += 20

        if "safety" in match.careena_decision_role:
            score += 10

        if match.urgency_effect == "requires_safety_clarification":
            score += 10

        if match.criterion_role in {"entry_criterion", "level_discriminator"}:
            score += 5

        if match.suggested_question_text:
            score += 5

        return score
