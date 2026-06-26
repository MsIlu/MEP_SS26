import sys
from pathlib import Path
from unittest.mock import MagicMock

SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain.safety_catalog import SafetyCatalogMatch
from careena4.models.turn import TurnInput


def _safety_match(term: str = "atemnot") -> SafetyCatalogMatch:
    return SafetyCatalogMatch(
        evidence_term=term,
        matched_lay_term=term.capitalize(),
        consultation_reason_source_id="1008",
        criterion_key="dyspnea_test",
        criterion_role="primary_criterion",
        urgency_effect="requires_safety_clarification",
        careena_decision_role="safety_relevant",
        is_safety_relevant=True,
        is_red_flag_candidate=True,
    )


def _engine_with_cache(*, terms: list[str]) -> TurnEngine:
    """Build a TurnEngine with a mocked catalog cache that fires for the given terms."""
    cache = MagicMock()
    cache.is_loaded = True
    cache.scan_text.return_value = [_safety_match(t) for t in terms]
    cache.scan_labels.return_value = []
    return TurnEngine(raw_red_flag_detector=RawRedFlagDetector(catalog_cache=cache))


def test_raw_suspected_dyspnea_opens_safety_question_without_emergency():
    engine = _engine_with_cache(terms=["atemnot"])

    result = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    assert result.response_mode == "ask_safety_question"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "safety_clarification"
    assert result.conversation_state.active_question.safety_context is not None
    assert result.conversation_state.active_question.blocking is True
    assert "turn:safety_clarification_opened" in result.trace_notes
    assert result.response_mode != "emergency"


def test_yes_to_open_safety_question_confirms_emergency():
    engine = _engine_with_cache(terms=["atemnot"])

    first = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    second = engine.run_turn(
        TurnInput(
            message="yes",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert second.response_mode == "emergency"
    assert "turn:safety_confirmation_emergency" in second.trace_notes


def test_no_to_open_safety_question_clears_question_without_emergency():
    engine = _engine_with_cache(terms=["atemnot"])

    first = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    second = engine.run_turn(
        TurnInput(
            message="no",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert second.response_mode != "emergency"
    assert second.conversation_state.active_question is None


def test_unsure_to_open_safety_question_keeps_question_open():
    engine = _engine_with_cache(terms=["atemnot"])

    first = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    second = engine.run_turn(
        TurnInput(
            message="unsure",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert second.response_mode == "ask_safety_question"
    assert second.conversation_state.active_question is not None
    assert second.conversation_state.active_question.kind == "safety_clarification"
    assert second.conversation_state.active_question.safety_context is not None
