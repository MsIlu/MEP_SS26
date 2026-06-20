from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus


def test_raw_critical_dyspnea_keine_luft_is_confirmed_emergency():
    safety = RawRedFlagDetector().detect("Ich bekomme keine Luft.")

    assert safety.red_flag_detected is True
    assert safety.red_flag_status == SafetyRedFlagStatus.CONFIRMED
    assert safety.action == SafetyAction.EMERGENCY
    assert safety.requires_emergency_response is True


def test_raw_negated_luftnot_is_not_misread_as_keine_luft_emergency():
    safety = RawRedFlagDetector().detect("Ich habe keine Luftnot.")

    assert safety.requires_emergency_response is False
    assert safety.requires_safety_clarification is False
