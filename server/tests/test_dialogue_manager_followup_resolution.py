# Test case references: documents/Testfaelle_Backend.md#t07-dialogue-und-response-management

import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena_pipeline3.application.managers.dialogue_manager import DialogueManager
from careena_pipeline3.application.managers.extraction_manager import ExtractionManager
from careena_pipeline3.application.managers.response_manager import ResponseManager
from careena_pipeline3.application.services import (
    ExtractionResultMapper,
    ResponseGenerationService,
)
from careena_pipeline3.models.domain import (
    CaseObservation,
    ConcernState,
    DialogueState,
    MedicalCase,
    PendingFollowup,
)
from careena_pipeline3.models.extraction import (
    Call2ExtractionResult,
    ExtractedObservation,
)
from careena_pipeline3.models.turn import EntryDecision, TurnInput


def test_dialogue_manager_does_not_repeat_answered_followup_question():
    persisted_case = MedicalCase(
        observations=[
            CaseObservation(
                id="obs-1",
                type="symptom",
                label="Kurzatmigkeit",
                display_label="schlecht Luft bekommen",
                source_span="schlecht Luft bekommen",
                subject_ref="self",
            )
        ],
        primary_problem_id="obs-1",
    )
    persisted_dialogue_state = DialogueState(
        pending_followup=PendingFollowup(
            requirement_key="symptom.duration_or_onset",
            slot="duration_or_onset",
            kind="requirement",
            focus_observation_id="obs-1",
            focus_label="schlecht Luft bekommen",
        ),
        active_modules=["symptom"],
    )
    turn_input = TurnInput(
        message="seit ein paar tagen",
        persisted_case=persisted_case,
        persisted_dialogue_state=persisted_dialogue_state,
        persisted_concern_state=ConcernState(),
    )

    manager = DialogueManager(
        entry_manager=_StubEntryManager(
            EntryDecision(
                extraction_required=True,
                message_role="answer_to_followup",
                call2_operation_mode="followup_slot_update",
                concern_relation="same_concern",
                latest_turn_role="medical_clarification",
                active_modules=["symptom"],
                call2_tasks=["resolve_subject_context", "extract_symptoms"],
            )
        ),
        extraction_manager=ExtractionManager(
            extraction_service=_StubExtractionService(
                Call2ExtractionResult(
                    case_extension_status="updates_existing_information",
                    focus_update=ExtractedObservation(
                        observation_id="obs-1",
                        raw_label="Kurzatmigkeit",
                        observation_type="symptom",
                        normalized_concept="dyspnea",
                        source_span="schlecht Luft bekommen",
                        subject_ref="self",
                        attributes={"temporality": "seit ein paar tagen"},
                    ),
                    trace_notes=["mode:followup_slot_update"],
                )
            ),
            extraction_result_mapper=ExtractionResultMapper(),
        ),
        response_manager=ResponseManager(
            response_generation_service=ResponseGenerationService()
        ),
    )

    result = manager.run_turn(turn_input)

    assert result.dialogue_state.pending_followup is None
    assert result.medical_case is not None
    assert result.medical_case.primary_observation() is not None
    assert result.medical_case.primary_observation().temporality == "seit ein paar tagen"
    assert result.response_text == "Danke, das hilft mir weiter."
    assert "Seit wann" not in result.response_text
    assert "process_state:answered_pending_followup:symptom.duration_or_onset" in result.trace_notes


class _StubEntryManager:
    def __init__(self, decision: EntryDecision) -> None:
        self._decision = decision

    def evaluate(self, turn_input, *, context=None) -> EntryDecision:
        return self._decision.model_copy(deep=True)


class _StubExtractionService:
    def __init__(self, result: Call2ExtractionResult) -> None:
        self._result = result

    def extract(self, text: str, **kwargs) -> Call2ExtractionResult:
        return self._result.model_copy(deep=True)
