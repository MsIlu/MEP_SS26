from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.turn import TurnInput


def _next_input(message: str, result):
    return TurnInput(
        message=message,
        persisted_case_topic=result.case_topic,
        persisted_medical_case=result.medical_case,
        persisted_conversation_state=result.conversation_state,
        persisted_recommendation_state=result.recommendation_state,
    )


def test_sparse_symptom_creates_subject_followup_first():
    engine = TurnEngine()

    result = engine.run_turn(TurnInput(message="Ich habe Bauchschmerzen."))

    assert result.response_mode == "ask_followup"
    assert result.case_topic is not None
    assert result.case_topic.current_label == "Bauchschmerzen"
    assert result.medical_case is not None
    assert len(result.medical_case.observations) == 1
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "subject_clarification"


def test_missing_subject_can_trigger_subject_clarification():
    engine = TurnEngine()

    result = engine.run_turn(TurnInput(message="Bauchschmerzen seit gestern."))

    assert result.response_mode == "ask_followup"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "subject_clarification"


def test_safety_signal_opens_safety_question():
    engine = TurnEngine()

    result = engine.run_turn(TurnInput(message="Ich habe Brustschmerzen und bekomme schlecht Luft."))

    assert result.response_mode == "ask_safety_question"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "safety_clarification"
