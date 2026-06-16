# Test case references: documents/Testfaelle_Backend.md#t06-safety-und-red-flags

import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena_pipeline3.application.services.safety_clarification_resolver import (
    SafetyClarificationResolver,
)
from careena_pipeline3.models.domain import PendingSafetyClarification
from careena_pipeline3.models.turn.safety_state import (
    SafetyAction,
    SafetyClarificationOutcome,
    SafetyRedFlagStatus,
)


def test_yes_confirms_red_flag_and_allows_emergency():
    resolver = SafetyClarificationResolver()
    pending = PendingSafetyClarification(evidence_terms=["schlecht luft"])

    resolution = resolver.resolve(pending=pending, answer_code="yes")

    assert resolution.outcome == SafetyClarificationOutcome.CONFIRMED_RED_FLAG
    assert resolution.safety_state.red_flag_status == SafetyRedFlagStatus.CONFIRMED
    assert resolution.safety_state.action == SafetyAction.EMERGENCY
    assert resolution.safety_state.requires_emergency_response is True
    assert resolution.clear_pending_clarification is True


def test_no_clears_suspected_red_flag():
    resolver = SafetyClarificationResolver()
    pending = PendingSafetyClarification(evidence_terms=["schlecht luft"])

    resolution = resolver.resolve(pending=pending, answer_code="no")

    assert resolution.outcome == SafetyClarificationOutcome.CLEARED_RED_FLAG
    assert (
        resolution.safety_state.red_flag_status
        == SafetyRedFlagStatus.CLARIFIED_NEGATIVE
    )
    assert resolution.safety_state.action == SafetyAction.NONE
    assert resolution.safety_state.requires_emergency_response is False
    assert resolution.clear_pending_clarification is True


def test_unsure_keeps_safety_clarification_open():
    resolver = SafetyClarificationResolver()
    pending = PendingSafetyClarification(evidence_terms=["schlecht luft"])

    resolution = resolver.resolve(pending=pending, answer_code="unsure")

    assert resolution.outcome == SafetyClarificationOutcome.STILL_UNCLEAR
    assert resolution.safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert resolution.safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert resolution.safety_state.requires_safety_clarification is True
    assert resolution.clear_pending_clarification is False


def test_immediate_help_confirms_emergency():
    resolver = SafetyClarificationResolver()
    pending = PendingSafetyClarification(evidence_terms=["schlecht luft"])

    resolution = resolver.resolve(pending=pending, answer_code="immediate_help")

    assert resolution.outcome == SafetyClarificationOutcome.CONFIRMED_EMERGENCY
    assert resolution.safety_state.red_flag_status == SafetyRedFlagStatus.CONFIRMED
    assert resolution.safety_state.action == SafetyAction.EMERGENCY
    assert resolution.safety_state.requires_emergency_response is True
    assert resolution.clear_pending_clarification is True


def test_invalid_answer_keeps_safety_clarification_open():
    resolver = SafetyClarificationResolver()
    pending = PendingSafetyClarification(evidence_terms=["schlecht luft"])

    resolution = resolver.resolve(pending=pending, answer_code="maybe")

    assert resolution.outcome == SafetyClarificationOutcome.INVALID_ANSWER
    assert resolution.safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert resolution.safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert resolution.clear_pending_clarification is False
    
def test_visible_label_yes_confirms_red_flag():
    resolver = SafetyClarificationResolver()
    pending = PendingSafetyClarification(evidence_terms=["schlecht luft"])

    resolution = resolver.resolve(pending=pending, answer_code="Ja")

    assert resolution.outcome == SafetyClarificationOutcome.CONFIRMED_RED_FLAG
    assert resolution.safety_state.red_flag_status == SafetyRedFlagStatus.CONFIRMED
    assert resolution.safety_state.action == SafetyAction.EMERGENCY
    assert resolution.clear_pending_clarification is True
