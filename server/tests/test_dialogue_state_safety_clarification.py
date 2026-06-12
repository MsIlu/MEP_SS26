import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena_pipeline3.application.managers.dialogue_manager import DialogueManager
from careena_pipeline3.models.turn import TurnContext
from careena_pipeline3.models.turn.safety_state import (
    SafetyAction,
    SafetyRedFlagStatus,
    SafetyState,
)


def test_dialogue_manager_stores_pending_safety_clarification():
    manager = DialogueManager()
    context = TurnContext()

    manager._apply_safety_state(
        context=context,
        stage="raw",
        safety_state=SafetyState(
            checked_sources=["raw_message"],
            red_flag_detected=True,
            red_flag_status=SafetyRedFlagStatus.SUSPECTED,
            action=SafetyAction.ASK_SAFETY_CLARIFICATION,
            evidence_terms=["schlecht luft"],
            clarification_question_code="raw_red_flag_clarification",
        ),
    )

    pending = context.dialogue_state.pending_safety_clarification

    assert pending is not None
    assert pending.kind == "red_flag_clarification"
    assert pending.question_code == "raw_red_flag_clarification"
    assert pending.source_stage == "raw"
    assert pending.evidence_terms == ["schlecht luft"]
    assert context.raw_safety.requires_safety_clarification is True