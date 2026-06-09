import sys
import unittest
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena_pipeline3.application.managers.dialogue_manager import DialogueManager
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.turn import (
    ConfirmationDecision,
    EntryDecision,
    ExtractionPayload,
    ProcessStateUpdate,
    ReadinessStateUpdate,
    ResponsePlan,
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
            recommendation_requested=True,
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
        )


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


if __name__ == "__main__":
    unittest.main()
