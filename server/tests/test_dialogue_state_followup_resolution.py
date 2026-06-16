# Test case references: documents/Testfaelle_Backend.md#t07-dialogue-und-response-management

import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena_pipeline3.application.services.dialogue_state_service import (
    DialogueStateService,
)
from careena_pipeline3.models.domain import (
    CaseObservation,
    DialogueState,
    MedicalCase,
    PendingFollowup,
)


def test_resolved_requirement_followup_creates_turn_local_resolution():
    service = DialogueStateService()
    dialogue_state = DialogueState()
    medical_case = MedicalCase(
        observations=[
            CaseObservation(
                id="obs-1",
                type="symptom",
                label="Kurzatmigkeit",
                display_label="schlecht Luft bekommen",
                source_span="schlecht Luft bekommen",
                temporality="seit ein paar tagen",
                subject_ref="self",
            )
        ]
    )
    previous_pending_followup = PendingFollowup(
        requirement_key="symptom.duration_or_onset",
        slot="duration_or_onset",
        kind="requirement",
        focus_observation_id="obs-1",
        focus_label="schlecht Luft bekommen",
    )

    update = service.sync_after_case_update(
        dialogue_state=dialogue_state,
        medical_case=medical_case,
        active_modules=["symptom"],
        previous_pending_followup=previous_pending_followup,
    )

    resolved = update.process_state_signals.resolved_followup

    assert resolved is not None
    assert resolved.requirement_key == "symptom.duration_or_onset"
    assert resolved.slot == "duration_or_onset"
    assert resolved.kind == "requirement"
    assert resolved.focus_observation_id == "obs-1"
    assert resolved.focus_label == "schlecht Luft bekommen"
    assert update.dialogue_state.pending_followup is None


def test_unresolved_followup_keeps_resolution_empty():
    service = DialogueStateService()
    dialogue_state = DialogueState()
    medical_case = MedicalCase(
        observations=[
            CaseObservation(
                id="obs-1",
                type="symptom",
                label="Kurzatmigkeit",
                source_span="schlecht Luft bekommen",
                subject_ref="self",
            )
        ]
    )
    previous_pending_followup = PendingFollowup(
        requirement_key="symptom.duration_or_onset",
        slot="duration_or_onset",
        kind="requirement",
        focus_observation_id="obs-1",
        focus_label="schlecht Luft bekommen",
    )

    update = service.sync_after_case_update(
        dialogue_state=dialogue_state,
        medical_case=medical_case,
        active_modules=["symptom"],
        previous_pending_followup=previous_pending_followup,
    )

    assert update.process_state_signals.resolved_followup is None
    assert update.dialogue_state.pending_followup is not None
    assert update.dialogue_state.pending_followup.slot == "duration_or_onset"


def test_additional_medical_information_signal_survives_followup_resolution():
    service = DialogueStateService()
    dialogue_state = DialogueState()
    medical_case = MedicalCase(
        observations=[
            CaseObservation(
                id="obs-1",
                type="symptom",
                label="Kurzatmigkeit",
                source_span="schlecht Luft bekommen",
                temporality="seit ein paar tagen",
                subject_ref="self",
            )
        ]
    )
    previous_pending_followup = PendingFollowup(
        requirement_key="symptom.duration_or_onset",
        slot="duration_or_onset",
        kind="requirement",
        focus_observation_id="obs-1",
        focus_label="schlecht Luft bekommen",
    )

    update = service.sync_after_case_update(
        dialogue_state=dialogue_state,
        medical_case=medical_case,
        active_modules=["symptom"],
        previous_pending_followup=previous_pending_followup,
        additional_medical_information=True,
    )

    assert update.process_state_signals.resolved_followup is not None
    assert update.process_state_signals.additional_medical_information_detected is True
    assert (
        "process_state:mixed_followup_and_additional_information"
        in update.process_state_signals.trace_notes
    )
