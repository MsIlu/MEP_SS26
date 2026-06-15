import sys
from pathlib import Path

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena_pipeline3.infrastructure.repositories.sql_safety_catalog_repository import (
    SqlSafetyCatalogRepository,
)
from database.catalog.models import (
    AssessmentCriterion,
    ConsultationReason,
    ConsultationReasonAssessmentCriterionLink,
)


def _build_test_session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def session_factory() -> Session:
        return Session(engine)

    return session_factory


def test_repository_finds_safety_catalog_match_by_lay_term():
    session_factory = _build_test_session_factory()

    with session_factory() as session:
        reason = ConsultationReason(
            source_system="STS",
            source_version="1.10",
            source_id="1008",
            source_category_de="Kardiovaskulär / Respiratorisch",
            source_label_de="Atemsymptome",
            careena_key="atemsymptome",
            is_active=True,
        )
        criterion = AssessmentCriterion(
            criterion_key="dyspnea_or_shortness_of_breath_reported",
            label_de="Atemnot oder Kurzatmigkeit berichtet",
            criterion_type="symptom",
            suggested_question_texts_json=(
                '{"de": ["Bekommen Sie aktuell schlecht Luft?"]}'
            ),
            lay_terms_json='{"de": ["schlecht Luft", "Atemnot", "Luftnot"]}',
            expected_value_type="boolean",
            suggested_input_mode="yes_no_buttons",
            free_text_allowed=True,
            observation_context="self_report",
            careena_capture_status="usable",
            careena_capture_method="self_report",
            careena_use_policy="ask_if_context_relevant",
            is_active=True,
        )

        session.add(reason)
        session.add(criterion)
        session.commit()
        session.refresh(reason)
        session.refresh(criterion)

        link = ConsultationReasonAssessmentCriterionLink(
            consultation_reason_id=reason.id,
            assessment_criterion_id=criterion.id,
            relevance="primary",
            is_safety_relevant=True,
            is_red_flag_candidate=True,
            careena_decision_role="safety_clarification_trigger",
            criterion_role="entry_criterion",
            urgency_effect="requires_safety_clarification",
            is_active=True,
        )

        session.add(link)
        session.commit()

    repository = SqlSafetyCatalogRepository(session_factory=session_factory)

    matches = repository.find_matches_for_evidence_terms(["schlecht luft"])

    assert len(matches) == 1

    match = matches[0]
    assert match.source_system == "STS"
    assert match.source_version == "1.10"
    assert match.consultation_reason_source_id == "1008"
    assert match.consultation_reason_key == "atemsymptome"
    assert match.consultation_reason_label_de == "Atemsymptome"
    assert match.criterion_key == "dyspnea_or_shortness_of_breath_reported"
    assert match.criterion_role == "entry_criterion"
    assert match.urgency_effect == "requires_safety_clarification"
    assert match.careena_decision_role == "safety_clarification_trigger"
    assert match.suggested_question_text == "Bekommen Sie aktuell schlecht Luft?"
    assert match.suggested_input_mode == "yes_no_buttons"
    assert match.free_text_allowed is True
    assert match.is_safety_relevant is True
    assert match.is_red_flag_candidate is True
    assert match.mapping_status == "catalog_matched"


def test_repository_ignores_non_safety_links():
    session_factory = _build_test_session_factory()

    with session_factory() as session:
        reason = ConsultationReason(
            source_system="STS",
            source_version="1.10",
            source_id="9999",
            source_label_de="Testgrund",
            careena_key="testgrund",
            is_active=True,
        )
        criterion = AssessmentCriterion(
            criterion_key="test_criterion",
            label_de="Testkriterium",
            criterion_type="symptom",
            lay_terms_json='{"de": ["testsignal"]}',
            careena_capture_status="usable",
            careena_capture_method="self_report",
            careena_use_policy="ask_if_context_relevant",
            is_active=True,
        )

        session.add(reason)
        session.add(criterion)
        session.commit()
        session.refresh(reason)
        session.refresh(criterion)

        link = ConsultationReasonAssessmentCriterionLink(
            consultation_reason_id=reason.id,
            assessment_criterion_id=criterion.id,
            is_safety_relevant=False,
            is_red_flag_candidate=False,
            careena_decision_role="supporting_context",
            criterion_role="supporting_criterion",
            urgency_effect="supporting_context_only",
            is_active=True,
        )

        session.add(link)
        session.commit()

    repository = SqlSafetyCatalogRepository(session_factory=session_factory)

    matches = repository.find_matches_for_evidence_terms(["testsignal"])

    assert matches == []