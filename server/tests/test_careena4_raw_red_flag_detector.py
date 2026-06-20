from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus


def test_careena4_detects_unclear_dyspnea_as_suspected_red_flag():
    safety_state = RawRedFlagDetector().detect("Ich bekomme schlecht Luft.")

    assert safety_state.red_flag_detected is True
    assert safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert safety_state.requires_safety_clarification is True
    assert safety_state.requires_emergency_response is False
    assert "schlecht luft" in safety_state.evidence_terms


def test_careena4_detects_chest_pain_as_suspected_red_flag():
    safety_state = RawRedFlagDetector().detect("Ich habe Brustschmerzen.")

    assert safety_state.red_flag_detected is True
    assert safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert safety_state.requires_emergency_response is False
    assert "brustschmerzen" in safety_state.evidence_terms


def test_careena4_detects_unconscious_and_not_breathing_as_confirmed_emergency():
    safety_state = RawRedFlagDetector().detect(
        "Die Person ist ohnmächtig und hört auf zu atmen."
    )

    assert safety_state.red_flag_detected is True
    assert safety_state.red_flag_status == SafetyRedFlagStatus.CONFIRMED
    assert safety_state.action == SafetyAction.EMERGENCY
    assert safety_state.requires_emergency_response is True
    assert "ohnmaechtig" in safety_state.evidence_terms
    assert "hoert auf zu atmen" in safety_state.evidence_terms


def test_careena4_does_not_flag_negated_dyspnea_or_chest_pain():
    safety_state = RawRedFlagDetector().detect(
        "Ich habe Husten, aber keine Atemnot und keine Brustschmerzen."
    )

    assert safety_state.red_flag_detected is False
    assert safety_state.red_flag_status == SafetyRedFlagStatus.NONE
    assert safety_state.action == SafetyAction.NONE
    assert safety_state.requires_emergency_response is False
    assert safety_state.requires_safety_clarification is False


def test_careena4_keine_luft_stays_suspected_for_clarification():
    safety_state = RawRedFlagDetector().detect("Ich bekomme keine Luft.")

    assert safety_state.red_flag_detected is True
    assert safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert safety_state.requires_safety_clarification is True
    assert "bekomme keine luft" in safety_state.evidence_terms


def test_careena4_detects_acute_neurologic_deficit_as_suspected_red_flag():
    safety_state = RawRedFlagDetector().detect(
        "Plötzlich hängt mein Mundwinkel und mein rechter Arm ist gelähmt."
    )

    assert safety_state.red_flag_detected is True
    assert safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert safety_state.requires_safety_clarification is True


def test_careena4_detects_altered_consciousness_as_suspected_red_flag():
    safety_state = RawRedFlagDetector().detect(
        "Mein Bruder ist kaum wach und reagiert kaum."
    )

    assert safety_state.red_flag_detected is True
    assert safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert safety_state.requires_safety_clarification is True


def test_careena4_does_not_flag_vague_feeling_as_raw_red_flag():
    safety_state = RawRedFlagDetector().detect("Mir ist irgendwie komisch.")

    assert safety_state.red_flag_detected is False
    assert safety_state.red_flag_status == SafetyRedFlagStatus.NONE
    assert safety_state.action == SafetyAction.NONE
    assert safety_state.requires_emergency_response is False
