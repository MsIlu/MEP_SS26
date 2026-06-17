import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena4.application.dialogue.safety_clarification_builder import (
    SafetyClarificationBuilder,
)
from careena4.models.domain import SafetyCatalogMatch
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus, SafetyState


class MatchingSafetyCatalogRepository:
    def find_matches_for_evidence_terms(
        self,
        evidence_terms: list[str],
    ) -> list[SafetyCatalogMatch]:
        return [
            SafetyCatalogMatch(
                evidence_term="schlecht luft",
                matched_lay_term="schlecht luft",
                source_system="STS",
                source_version="1.10",
                consultation_reason_source_id="1008",
                consultation_reason_key="respiratory_symptoms",
                consultation_reason_label_de="Atemsymptome",
                criterion_key="dyspnea_or_shortness_of_breath_reported",
                criterion_label_de="Atemnot oder Kurzatmigkeit berichtet",
                criterion_role="entry_criterion",
                urgency_effect="requires_safety_clarification",
                careena_decision_role="safety_clarification",
                suggested_question_text=(
                    "Bekommen Sie schlecht Luft oder sind Sie kurzatmig?"
                ),
                suggested_input_mode="structured_required",
                free_text_allowed=False,
                is_safety_relevant=True,
                is_red_flag_candidate=True,
                mapping_status="catalog_matched",
            )
        ]


class EmptySafetyCatalogRepository:
    def find_matches_for_evidence_terms(
        self,
        evidence_terms: list[str],
    ) -> list[SafetyCatalogMatch]:
        return []


class FailingSafetyCatalogRepository:
    def find_matches_for_evidence_terms(
        self,
        evidence_terms: list[str],
    ) -> list[SafetyCatalogMatch]:
        raise RuntimeError("database unavailable")


def suspected_safety_state() -> SafetyState:
    return SafetyState(
        checked_sources=["raw_message"],
        red_flag_detected=True,
        red_flag_status=SafetyRedFlagStatus.SUSPECTED,
        action=SafetyAction.ASK_SAFETY_CLARIFICATION,
        severity="unclear",
        evidence_terms=["schlecht luft"],
        clarification_question_code="raw_red_flag_clarification",
    )


def test_builder_preserves_safety_context_from_catalog_match():
    builder = SafetyClarificationBuilder(
        safety_catalog_repository=MatchingSafetyCatalogRepository()
    )

    question = builder.build_active_question(safety_state=suspected_safety_state())

    assert question.kind == "safety_clarification"
    assert question.safety_context is not None
    assert question.prompt_text == "Bekommen Sie schlecht Luft oder sind Sie kurzatmig?"

    context = question.safety_context
    assert context.question_code == "raw_red_flag_clarification"
    assert context.source_stage == "raw_message"
    assert context.evidence_terms == ["schlecht luft"]
    assert context.source_system == "STS"
    assert context.source_version == "1.10"
    assert context.consultation_reason_source_id == "1008"
    assert context.consultation_reason_key == "respiratory_symptoms"
    assert context.consultation_reason_label_de == "Atemsymptome"
    assert context.criterion_key == "dyspnea_or_shortness_of_breath_reported"
    assert context.criterion_role == "entry_criterion"
    assert context.urgency_effect == "requires_safety_clarification"
    assert context.careena_decision_role == "safety_clarification"
    assert context.catalog_mapping_status == "catalog_matched"
    assert context.matched_lay_term == "schlecht luft"

    # Compatibility bridge for existing resolver code.
    assert question.safety_question_code == context.question_code
    assert question.safety_evidence_terms == context.evidence_terms


def test_builder_marks_no_repository_fallback_in_safety_context():
    builder = SafetyClarificationBuilder(safety_catalog_repository=None)

    question = builder.build_active_question(safety_state=suspected_safety_state())

    assert question.safety_context is not None
    assert question.safety_context.catalog_mapping_status == "fallback_no_catalog_repository"
    assert question.safety_context.source_system == "STS"


def test_builder_marks_no_catalog_match_fallback_in_safety_context():
    builder = SafetyClarificationBuilder(
        safety_catalog_repository=EmptySafetyCatalogRepository()
    )

    question = builder.build_active_question(safety_state=suspected_safety_state())

    assert question.safety_context is not None
    assert question.safety_context.catalog_mapping_status == "fallback_no_catalog_match"
    assert question.safety_context.consultation_reason_source_id is None
    assert question.safety_context.criterion_key is None


def test_builder_marks_catalog_unavailable_fallback_in_safety_context():
    builder = SafetyClarificationBuilder(
        safety_catalog_repository=FailingSafetyCatalogRepository()
    )

    question = builder.build_active_question(safety_state=suspected_safety_state())

    assert question.safety_context is not None
    assert question.safety_context.catalog_mapping_status == "fallback_catalog_unavailable"
    assert question.safety_context.consultation_reason_source_id is None
    assert question.safety_context.criterion_key is None
