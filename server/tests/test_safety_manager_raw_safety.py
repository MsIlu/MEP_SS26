# Test case references: documents/Testfaelle_Backend.md#t06-safety-und-red-flags

import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena_pipeline3.application.managers.safety_manager import SafetyManager
from careena_pipeline3.models.turn import TurnInput
from careena_pipeline3.models.turn.safety_state import (
    SafetyAction,
    SafetyRedFlagStatus,
)


def test_safety_manager_uses_raw_detector_for_suspected_red_flag():
    manager = SafetyManager()

    safety_state = manager.assess_raw_message(
        TurnInput(message="Ich bekomme schlecht Luft.")
    )

    assert safety_state.red_flag_detected is True
    assert safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert safety_state.requires_safety_clarification is True
    assert safety_state.requires_emergency_response is False


def test_safety_manager_keeps_non_red_flag_message_clear():
    manager = SafetyManager()

    safety_state = manager.assess_raw_message(
        TurnInput(message="Mir ist irgendwie komisch.")
    )

    assert safety_state.red_flag_detected is False
    assert safety_state.red_flag_status == SafetyRedFlagStatus.NONE
    assert safety_state.action == SafetyAction.NONE
    assert safety_state.requires_emergency_response is False
