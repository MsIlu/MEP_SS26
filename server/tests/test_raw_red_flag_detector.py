import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena_pipeline3.application.services.raw_red_flag_detector import (
    RawRedFlagDetector,
)
from careena_pipeline3.models.turn.safety_state import (
    SafetyAction,
    SafetyRedFlagStatus,
)


def test_detects_unclear_dyspnea_as_suspected_red_flag():
    detector = RawRedFlagDetector()

    safety_state = detector.detect("Ich bekomme schlecht Luft.")

    assert safety_state.red_flag_detected is True
    assert safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert safety_state.requires_safety_clarification is True
    assert safety_state.requires_emergency_response is False
    assert "schlecht luft" in safety_state.evidence_terms


def test_detects_chest_pain_as_suspected_red_flag():
    detector = RawRedFlagDetector()

    safety_state = detector.detect("Ich habe Brustschmerzen.")

    assert safety_state.red_flag_detected is True
    assert safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert safety_state.requires_emergency_response is False


def test_detects_unconscious_and_not_breathing_as_confirmed_emergency():
    detector = RawRedFlagDetector()

    safety_state = detector.detect("Die Person ist bewusstlos und atmet nicht.")

    assert safety_state.red_flag_detected is True
    assert safety_state.red_flag_status == SafetyRedFlagStatus.CONFIRMED
    assert safety_state.action == SafetyAction.EMERGENCY
    assert safety_state.requires_emergency_response is True


def test_does_not_flag_vague_feeling_as_raw_red_flag():
    detector = RawRedFlagDetector()

    safety_state = detector.detect("Mir ist irgendwie komisch.")

    assert safety_state.red_flag_detected is False
    assert safety_state.red_flag_status == SafetyRedFlagStatus.NONE
    assert safety_state.action == SafetyAction.NONE
    assert safety_state.requires_emergency_response is False