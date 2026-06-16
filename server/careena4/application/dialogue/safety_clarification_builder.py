import logging

from careena4.application.repositories.safety_catalog_repository import SafetyCatalogRepository
from careena4.models.domain import (
    ActiveQuestion,
    GuidedInputContract,
    GuidedInputMode,
    GuidedInputOption,
    SafetyCatalogMatch,
    SafetyQuestionContext,
)
from careena4.models.turn import SafetyState


logger = logging.getLogger(__name__)


class SafetyClarificationBuilder:
    def __init__(
        self,
        safety_catalog_repository: SafetyCatalogRepository | None = None,
    ):
        self.safety_catalog_repository = safety_catalog_repository

    def build_active_question(self, *, safety_state: SafetyState) -> ActiveQuestion:
        question_code = (
            safety_state.clarification_question_code
            or "raw_red_flag_clarification"
        )
        evidence_terms = list(safety_state.evidence_terms)

        if self.safety_catalog_repository is None or not evidence_terms:
            return self._fallback_question(
                prompt_text="Ich moechte kurz eine sicherheitsrelevante Angabe klaeren.",
                question_code=question_code,
                evidence_terms=evidence_terms,
                catalog_mapping_status="fallback_no_catalog_repository",
            )

        try:
            match = self._find_best_catalog_match(evidence_terms)
        except Exception:
            logger.exception("Safety catalog lookup failed; using generic fallback.")
            return self._fallback_question(
                prompt_text="Ich moechte kurz eine sicherheitsrelevante Angabe klaeren.",
                question_code=question_code,
                evidence_terms=evidence_terms,
                catalog_mapping_status="fallback_catalog_unavailable",
            )

        if match is not None and match.suggested_question_text:
            return self._question_from_match(
                match=match,
                question_code=question_code,
                evidence_terms=evidence_terms,
            )

        return self._fallback_question(
            prompt_text="Ich moechte kurz eine sicherheitsrelevante Angabe klaeren.",
            question_code=question_code,
            evidence_terms=evidence_terms,
            catalog_mapping_status="fallback_no_catalog_match",
        )

    def _find_best_catalog_match(
        self,
        evidence_terms: list[str],
    ) -> SafetyCatalogMatch | None:
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
        # Score by generic safety metadata, never by symptom identity.
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

    @classmethod
    def _question_from_match(
        cls,
        *,
        match: SafetyCatalogMatch,
        question_code: str,
        evidence_terms: list[str],
    ) -> ActiveQuestion:
        safety_context = SafetyQuestionContext(
            question_code=question_code,
            source_stage="raw_message",
            evidence_terms=evidence_terms,
            source_system=match.source_system,
            source_version=match.source_version,
            consultation_reason_source_id=match.consultation_reason_source_id,
            consultation_reason_key=match.consultation_reason_key,
            consultation_reason_label_de=match.consultation_reason_label_de,
            criterion_key=match.criterion_key,
            criterion_label_de=match.criterion_label_de,
            criterion_role=match.criterion_role,
            urgency_effect=match.urgency_effect,
            careena_decision_role=match.careena_decision_role,
            catalog_mapping_status=match.mapping_status or "catalog_matched",
            matched_lay_term=match.matched_lay_term,
        )
        return cls._base_question(
            prompt_text=match.suggested_question_text
            or "Ich moechte kurz eine sicherheitsrelevante Angabe klaeren.",
            safety_context=safety_context,
        )

    @classmethod
    def _fallback_question(
        cls,
        *,
        prompt_text: str,
        question_code: str,
        evidence_terms: list[str],
        catalog_mapping_status: str,
    ) -> ActiveQuestion:
        safety_context = SafetyQuestionContext(
            question_code=question_code,
            source_stage="raw_message",
            evidence_terms=evidence_terms,
            source_system="STS",
            catalog_mapping_status=catalog_mapping_status,
        )
        return cls._base_question(
            prompt_text=prompt_text,
            safety_context=safety_context,
        )

    @staticmethod
    def _base_question(
        *,
        prompt_text: str,
        safety_context: SafetyQuestionContext,
    ) -> ActiveQuestion:
        return ActiveQuestion(
            kind="safety_clarification",
            question_intent="free_description",
            prompt_text=prompt_text,
            blocking=True,
            allows_additional_medical_info=False,
            safety_question_code=safety_context.question_code,
            safety_evidence_terms=list(safety_context.evidence_terms),
            safety_context=safety_context,
            guided_input=GuidedInputContract(
                mode=GuidedInputMode.STRUCTURED_REQUIRED,
                free_text_allowed=False,
                options=[
                    GuidedInputOption(
                        code="yes",
                        label="Ja",
                        effect_code="confirms_red_flag",
                    ),
                    GuidedInputOption(
                        code="no",
                        label="Nein",
                        effect_code="clears_red_flag",
                    ),
                    GuidedInputOption(
                        code="unsure",
                        label="Ich bin unsicher",
                        effect_code="keeps_clarification_open",
                    ),
                    GuidedInputOption(
                        code="immediate_help",
                        label="Ich brauche sofort Hilfe",
                        effect_code="confirms_emergency",
                    ),
                ],
            ),
        )
