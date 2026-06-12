import sys
import types
import unittest
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

sys.modules.setdefault("openai", types.SimpleNamespace(OpenAI=object))
sys.modules.setdefault(
    "dotenv",
    types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None),
)


from careena_pipeline3.application.managers.dialogue_manager import DialogueManager
from careena_pipeline3.application.services.concern_state_service import ConcernStateService
from careena_pipeline3.application.services.dialogue_state_service import DialogueStateService
from careena_pipeline3.models.domain import (
    CaseObservation,
    ConcernState,
    DialogueState,
    MedicalCase,
    PendingFollowup,
)
from careena_pipeline3.models.turn import (
    ConfirmationDecision,
    EntryDecision,
    ExtractionPayload,
    ProcessStateSignals,
    ProcessStateUpdate,
    ReadinessStateUpdate,
    ResponsePlan,
    ResponseState,
    SafetyState,
    TurnInput,
)
from careena_pipeline3.models.workflow import AssessmentReadiness, RecommendationResult


class StubEntryManager:
    def __init__(self, calls):
        self.calls = calls

    def evaluate(self, turn_input, *, context=None):
        self.calls.append("entry")
        return EntryDecision(
            extraction_required=True,
            recommendation_requested=True,
            active_modules=["symptom"],
            trace_notes=["entry_trace"],
        )


class StubExtractionManager:
    def __init__(self, calls):
        self.calls = calls

    def extract(self, *, turn_input, entry_decision, context):
        self.calls.append("extraction")
        return ExtractionPayload(
            active_modules=["symptom"],
            trace_notes=["extraction_trace"],
        )


class StubCaseStateManager:
    def __init__(self, calls):
        self.calls = calls

    def ensure_case_context(self, *, context):
        self.calls.append("ensure_case")
        if context.medical_case is None:
            context.medical_case = MedicalCase()
        return context

    def apply_extraction(self, *, context, extraction_payload):
        self.calls.append("case_truth")
        context.active_modules = list(extraction_payload.active_modules)
        context.case_update_dialogue_consequences = ["case_progressed"]
        context.trace_notes.extend(extraction_payload.trace_notes)
        return context


class StubDialogueStateService:
    def __init__(self, calls):
        self.calls = calls

    def sync_after_case_update(self, **kwargs):
        self.calls.append("process_state")
        dialogue_state = kwargs["dialogue_state"]
        dialogue_state.active_modules = list(kwargs["active_modules"])
        return ProcessStateUpdate(
            dialogue_state=dialogue_state,
            pending_followup=dialogue_state.pending_followup,
            process_state_signals=ProcessStateSignals(),
        )


class StubConcernStateService:
    def __init__(self, calls):
        self.calls = calls

    def ensure_state(self, concern_state):
        self.calls.append("ensure_concern")
        return concern_state if concern_state is not None else ConcernState()

    def sync_after_case_update(self, *, concern_state, medical_case):
        self.calls.append("sync_concern")
        concern_state.notes.append("synced")
        return concern_state, ["concern_trace"]


class StubRecommendationStateService:
    def __init__(self, calls):
        self.calls = calls

    def sync_dialogue_state(self, **kwargs):
        self.calls.append("readiness")
        dialogue_state = kwargs["dialogue_state"]
        dialogue_state.recommendation_ready = True
        return ReadinessStateUpdate(
            dialogue_state=dialogue_state,
            assessment_readiness=AssessmentReadiness(
                ready=True,
                has_medical_problem=True,
                reason_tags=["ready_for_recommendation"],
            ),
            pending_followup=dialogue_state.pending_followup,
        )


class StubSafetyManager:
    def __init__(self, calls):
        self.calls = calls

    def assess_raw_message(self, turn_input):
        self.calls.append("raw_safety")
        return SafetyState(trace_notes=["raw_safety_trace"])

    def assess_extraction(self, extraction_payload):
        self.calls.append("extraction_safety")
        return SafetyState(trace_notes=["extraction_safety_trace"])

    def assess_case(self, medical_case):
        self.calls.append("case_safety")
        return SafetyState(trace_notes=["case_safety_trace"])


class StubResponseManager:
    def __init__(self, calls):
        self.calls = calls

    def plan(self, **kwargs):
        self.calls.append("response")
        return ResponsePlan(
            response_mode="recommend",
            response_state=ResponseState(
                selected_response_mode="recommend",
                medical_state="sufficient_information",
                recommendation_state="ready_for_recommendation",
            ),
            response_text="Empfehlung bereit.",
            recommendation_result=RecommendationResult(
                allowed=True,
                summary="Kurzempfehlung",
            ),
            trace_notes=["response_trace"],
        )


class StubConfirmationManager:
    def __init__(self, calls):
        self.calls = calls

    def evaluate(self, context):
        self.calls.append("confirmation")
        return ConfirmationDecision(
            should_request_confirmation=False,
            trace_notes=["confirmation_trace"],
        )


class DialogueManagerOrchestrationTest(unittest.TestCase):
    def test_run_turn_applies_staged_contracts_and_returns_context_response_truth(self):
        calls = []
        manager = DialogueManager(
            entry_manager=StubEntryManager(calls),
            extraction_manager=StubExtractionManager(calls),
            case_state_manager=StubCaseStateManager(calls),
            safety_manager=StubSafetyManager(calls),
            response_manager=StubResponseManager(calls),
            confirmation_manager=StubConfirmationManager(calls),
            dialogue_state_service=StubDialogueStateService(calls),
            recommendation_state_service=StubRecommendationStateService(calls),
        )

        result = manager.run_turn(
            TurnInput(
                message="Ich habe Kopfschmerzen.",
                session_id="test-session",
                conversation_messages=[],
                existing_case=MedicalCase(),
                existing_dialogue_state=DialogueState(),
            )
        )

        self.assertEqual(
            calls,
            [
                "raw_safety",
                "ensure_case",
                "entry",
                "extraction",
                "extraction_safety",
                "case_truth",
                "process_state",
                "readiness",
                "case_safety",
                "response",
                "confirmation",
            ],
        )
        self.assertEqual(result.response_mode, "recommend")
        self.assertEqual(result.response_text, "Empfehlung bereit.")
        self.assertIsNotNone(result.recommendation_result)
        self.assertEqual(result.recommendation_result.summary, "Kurzempfehlung")
        self.assertEqual(result.context.response_mode, "recommend")
        self.assertEqual(
            result.context.response_state.selected_response_mode,
            "recommend",
        )
        self.assertEqual(
            result.context.response_state.recommendation_state,
            "ready_for_recommendation",
        )
        self.assertEqual(result.context.response_text, "Empfehlung bereit.")
        self.assertIsNotNone(result.context.recommendation_result)
        self.assertEqual(result.context.recommendation_result.summary, "Kurzempfehlung")
        self.assertTrue(result.context.dialogue_state.recommendation_requested)
        self.assertTrue(result.context.dialogue_state.recommendation_ready)
        self.assertEqual(result.context.active_modules, ["symptom"])
        self.assertEqual(
            result.context.trace_notes,
            [
                "raw_safety_trace",
                "entry_trace",
                "extraction_safety_trace",
                "extraction_trace",
                "case_safety_trace",
                "response_trace",
                "confirmation_trace",
            ],
        )

    def test_dialogue_state_service_exposes_answered_followup_and_parallel_additional_info(self):
        service = DialogueStateService()
        focus = CaseObservation(
            type="symptom",
            label="Husten",
            display_label="Husten",
            source_span="Husten",
            temporality="seit gestern",
        )
        additional = CaseObservation(
            type="symptom",
            label="Fieber",
            display_label="Fieber",
            source_span="Fieber",
        )
        medical_case = MedicalCase(
            observations=[focus, additional],
            primary_problem_id=focus.id,
        )
        pending_followup = PendingFollowup(
            requirement_key="symptom.duration_or_onset",
            slot="duration_or_onset",
            kind="requirement",
            focus_observation_id=focus.id,
            focus_label=focus.patient_label,
        )
        dialogue_state = DialogueState(
            active_modules=["symptom"],
            pending_followup=pending_followup,
            focus_observation_id=focus.id,
            focus_label=focus.patient_label,
        )

        update = service.sync_after_case_update(
            dialogue_state=dialogue_state,
            medical_case=medical_case,
            active_modules=["symptom"],
            previous_pending_followup=pending_followup,
            additional_medical_information=True,
        )

        self.assertTrue(update.process_state_signals.answered_pending_followup)
        self.assertEqual(
            update.process_state_signals.answered_requirement_key,
            "symptom.duration_or_onset",
        )
        self.assertEqual(
            update.process_state_signals.answered_slot,
            "duration_or_onset",
        )
        self.assertTrue(
            update.process_state_signals.additional_medical_information_detected
        )
        self.assertIsNone(update.pending_followup)
        self.assertIn(
            "process_state:mixed_followup_and_additional_information",
            update.process_state_signals.trace_notes,
        )

    def test_run_turn_threads_existing_concern_state_through_context(self):
        calls = []
        manager = DialogueManager(
            entry_manager=StubEntryManager(calls),
            extraction_manager=StubExtractionManager(calls),
            case_state_manager=StubCaseStateManager(calls),
            safety_manager=StubSafetyManager(calls),
            response_manager=StubResponseManager(calls),
            confirmation_manager=StubConfirmationManager(calls),
            concern_state_service=StubConcernStateService(calls),
            dialogue_state_service=StubDialogueStateService(calls),
            recommendation_state_service=StubRecommendationStateService(calls),
        )
        concern_state = ConcernState(
            summary="Abklaerung mehrerer Beschwerden",
            linked_observation_ids=["kept-id"],
        )

        result = manager.run_turn(
            TurnInput(
                message="Ich habe Kopfschmerzen.",
                session_id="test-session",
                conversation_messages=[],
                existing_case=MedicalCase(),
                existing_dialogue_state=DialogueState(),
                existing_concern_state=concern_state,
            )
        )

        self.assertEqual(
            calls,
            [
                "ensure_concern",
                "raw_safety",
                "ensure_case",
                "entry",
                "extraction",
                "extraction_safety",
                "case_truth",
                "sync_concern",
                "process_state",
                "readiness",
                "case_safety",
                "response",
                "confirmation",
            ],
        )
        self.assertEqual(
            result.context.concern_state.summary,
            "Abklaerung mehrerer Beschwerden",
        )
        self.assertIn("synced", result.context.concern_state.notes)
        self.assertIn("concern_trace", result.context.trace_notes)


class ConcernStateServiceTest(unittest.TestCase):
    def test_sync_after_case_update_prunes_missing_observation_links(self):
        service = ConcernStateService()
        kept = CaseObservation(
            type="symptom",
            label="Husten",
            display_label="Husten",
            source_span="Husten",
        )
        medical_case = MedicalCase(observations=[kept])
        concern_state = ConcernState(
            linked_observation_ids=[kept.id, "missing-id"],
        )

        synced_state, trace_notes = service.sync_after_case_update(
            concern_state=concern_state,
            medical_case=medical_case,
        )

        self.assertEqual(synced_state.linked_observation_ids, [kept.id])
        self.assertEqual(
            trace_notes,
            ["concern_state:pruned_missing_observation_links"],
        )


if __name__ == "__main__":
    unittest.main()
