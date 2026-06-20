import pytest
from careena4.application.dialogue.question_resolver import QuestionResolver
from careena4.application.dialogue.safety_clarification_builder import SafetyClarificationBuilder
from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain import ConversationState
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus, SafetyState, TurnInput


class FailingQuestionResolver:
    def resolve(self, **kwargs):
        raise AssertionError(
            "Normal QuestionResolver must not resolve safety clarification answers."
        )


def _open_safety_clarification_state() -> ConversationState:
    active_question = SafetyClarificationBuilder().build_active_question(
        safety_state=SafetyState(
            checked_sources=["test"],
            red_flag_detected=True,
            red_flag_status=SafetyRedFlagStatus.SUSPECTED,
            action=SafetyAction.ASK_SAFETY_CLARIFICATION,
            evidence_terms=["Atemnot"],
            clarification_question_code="test_red_flag_clarification",
        )
    )
    return ConversationState(
        phase="followup",
        active_question=active_question,
    )


def test_open_safety_clarification_does_not_use_normal_question_resolver():
    result = TurnEngine(
        question_resolver=FailingQuestionResolver(),
    ).run_turn(
        TurnInput(
            message="Nein",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=_open_safety_clarification_state(),
        )
    )

    assert result.response_mode != "emergency"
    assert result.response_mode != "ask_safety_question"
    assert result.conversation_state.active_question is None
    assert "safety_clarification:cleared_red_flag" in result.trace_notes

def test_normal_question_resolver_rejects_safety_clarification_questions():
    active_question = _open_safety_clarification_state().active_question

    with pytest.raises(ValueError, match="Safety clarification"):
        QuestionResolver().resolve(
            question=active_question,
            message="Nein",
        )
