# Test case references: documents/Testfaelle_Backend.md#t06-safety-und-red-flags

from careena_pipeline3.application.services import SafetyClarificationBuilder
from careena_pipeline3.models.turn import SafetyState


class FailingSafetyCatalogRepository:
    """Test repository that simulates an unavailable catalog backend."""

    def find_matches_for_evidence_terms(self, evidence_terms: list[str]):
        """Raise an error like a database timeout or missing table would."""
        raise TimeoutError("catalog unavailable")


def test_safety_clarification_builder_falls_back_when_catalog_lookup_fails():
    builder = SafetyClarificationBuilder(
        safety_catalog_repository=FailingSafetyCatalogRepository()
    )

    pending = builder.build_pending_clarification(
        safety_state=SafetyState(
            evidence_terms=["schlecht luft"],
            clarification_question_code="raw_red_flag_clarification",
        ),
        source_stage="raw",
    )

    assert pending.kind == "red_flag_clarification"
    assert pending.question_code == "raw_red_flag_clarification"
    assert pending.source_stage == "raw"
    assert pending.evidence_terms == ["schlecht luft"]
    assert pending.question_text is None
    assert pending.source_system == "STS"
    assert pending.catalog_mapping_status == "fallback_catalog_unavailable"



class UnavailableDatabaseSafetyCatalogRepository:
    """Test repository that simulates an unavailable database connection."""

    def find_matches_for_evidence_terms(self, evidence_terms: list[str]):
        """Raise a connection error like an unavailable database would."""
        raise ConnectionError("database connection unavailable")


def test_safety_clarification_builder_falls_back_when_database_connection_is_unavailable():
    builder = SafetyClarificationBuilder(
        safety_catalog_repository=UnavailableDatabaseSafetyCatalogRepository()
    )

    pending = builder.build_pending_clarification(
        safety_state=SafetyState(
            evidence_terms=["schlecht luft"],
            clarification_question_code="raw_red_flag_clarification",
        ),
        source_stage="raw",
    )

    assert pending.kind == "red_flag_clarification"
    assert pending.question_code == "raw_red_flag_clarification"
    assert pending.source_stage == "raw"
    assert pending.evidence_terms == ["schlecht luft"]
    assert pending.question_text is None
    assert pending.source_system == "STS"
    assert pending.catalog_mapping_status == "fallback_catalog_unavailable"
