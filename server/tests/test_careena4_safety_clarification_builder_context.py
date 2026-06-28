import sys
from pathlib import Path
from unittest.mock import MagicMock


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena4.application.dialogue.safety_clarification_builder import (
    SafetyClarificationBuilder,
    _FALLBACK_QUESTION,
)
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus, SafetyState


def suspected_state(evidence_terms: list[str] | None = None) -> SafetyState:
    return SafetyState(
        checked_sources=["safety_pipeline"],
        red_flag_detected=True,
        red_flag_status=SafetyRedFlagStatus.SUSPECTED,
        action=SafetyAction.ASK_SAFETY_CLARIFICATION,
        severity="unclear",
        evidence_terms=evidence_terms if evidence_terms is not None else ["Atemnot"],
        clarification_question_code="raw_red_flag_clarification",
    )


def test_builder_uses_medgemma_question_when_llm_available():
    llm = MagicMock()
    llm.complete.return_value = "Bekommen Sie gerade Schwierigkeiten beim Atmen?"
    builder = SafetyClarificationBuilder(llm_client=llm)

    question = builder.build_active_question(safety_state=suspected_state())

    assert question.prompt_text == "Bekommen Sie gerade Schwierigkeiten beim Atmen?"
    assert question.safety_context.catalog_mapping_status == "medgemma_generated"
    llm.complete.assert_called_once()


def test_builder_falls_back_when_no_llm():
    builder = SafetyClarificationBuilder(llm_client=None)

    question = builder.build_active_question(safety_state=suspected_state())

    assert question.prompt_text == _FALLBACK_QUESTION
    assert question.safety_context.catalog_mapping_status == "fallback"


def test_builder_falls_back_when_llm_raises():
    llm = MagicMock()
    llm.complete.side_effect = RuntimeError("LLM unavailable")
    builder = SafetyClarificationBuilder(llm_client=llm)

    question = builder.build_active_question(safety_state=suspected_state())

    assert question.prompt_text == _FALLBACK_QUESTION


def test_builder_falls_back_when_llm_returns_empty():
    llm = MagicMock()
    llm.complete.return_value = "   "
    builder = SafetyClarificationBuilder(llm_client=llm)

    question = builder.build_active_question(safety_state=suspected_state())

    assert question.prompt_text == _FALLBACK_QUESTION


def test_builder_falls_back_when_no_evidence_terms():
    llm = MagicMock()
    builder = SafetyClarificationBuilder(llm_client=llm)

    question = builder.build_active_question(safety_state=suspected_state(evidence_terms=[]))

    assert question.prompt_text == _FALLBACK_QUESTION
    assert question.safety_context.catalog_mapping_status == "fallback"
    llm.complete.assert_not_called()


def test_builder_sets_correct_safety_context_fields():
    builder = SafetyClarificationBuilder(llm_client=None)

    question = builder.build_active_question(safety_state=suspected_state(["Atemnot", "Brustschmerzen"]))

    ctx = question.safety_context
    assert ctx.question_code == "raw_red_flag_clarification"
    assert ctx.source_stage == "case_slice"
    assert ctx.evidence_terms == ["Atemnot", "Brustschmerzen"]
    assert ctx.source_system == "STS"
    assert question.safety_question_code == ctx.question_code
    assert question.safety_evidence_terms == ctx.evidence_terms


def test_builder_guided_input_has_four_options():
    builder = SafetyClarificationBuilder(llm_client=None)

    question = builder.build_active_question(safety_state=suspected_state())

    options = question.guided_input.options
    effect_codes = {opt.effect_code for opt in options}
    assert len(options) == 4
    assert effect_codes == {
        "confirms_red_flag",
        "clears_red_flag",
        "keeps_clarification_open",
        "confirms_emergency",
    }
    assert question.guided_input.free_text_allowed is False


def test_builder_question_is_safety_clarification_kind():
    builder = SafetyClarificationBuilder()

    question = builder.build_active_question(safety_state=suspected_state())

    assert question.kind == "safety_clarification"
    assert question.blocking is True
