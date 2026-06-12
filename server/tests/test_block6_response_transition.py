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
from careena_pipeline3.application.managers.entry_manager import EntryManager
from careena_pipeline3.application.managers.response_manager import ResponseManager
from careena_pipeline3.application.services.recommendation_transition_service import (
    RecommendationTransitionService,
)
from careena_pipeline3.models.domain import (
    CaseObservation,
    DialogueState,
    MedicalCase,
    PendingDialogueTransition,
)
from careena_pipeline3.models.turn import (
    ConfirmationDecision,
    ExtractionPayload,
    ProcessStateSignals,
    ProcessStateUpdate,
    ReadinessStateUpdate,
    SafetyState,
    TurnInput,
)
from careena_pipeline3.models.workflow import IntentGateway
from careena_pipeline3.models.workflow import AssessmentReadiness
from careena_pipeline3.models.workflow import RecommendationTransitionResolution


class TrackingIntentClassificationService:
    def __init__(self):
        self.called = False

    def classify(self, **kwargs):
        self.called = True
        raise AssertionError(
            "intent classification should be bypassed for resolved recommendation transition"
        )


class FixedIntentClassificationService:
    def __init__(self, gateway):
        self.gateway = gateway
        self.called = False

    def classify(self, **kwargs):
        self.called = True
        return self.gateway


class FixedRecommendationTransitionService:
    def __init__(self, resolution):
        self.resolution = resolution
        self.called = False

    def resolve(self, **kwargs):
        self.called = True
        return self.resolution


class NullRecommendationTransitionService:
    def __init__(self):
        self.called = False

    def resolve(self, **kwargs):
        self.called = True
        return None


class StubCaseStateManager:
    def ensure_case_context(self, *, context):
        if context.medical_case is None:
            context.medical_case = MedicalCase()
        return context

    def apply_extraction(self, *, context, extraction_payload):
        return context


class StubExtractionManager:
    def extract(self, *, turn_input, entry_decision, context):
        if not entry_decision.extraction_required:
            return ExtractionPayload(trace_notes=["extraction_skipped"])
        raise AssertionError("extraction should be skipped when guide-next-step is resolved with no")


class StubDialogueStateService:
    def sync_after_case_update(self, **kwargs):
        dialogue_state = kwargs["dialogue_state"]
        return ProcessStateUpdate(
            dialogue_state=dialogue_state,
            pending_followup=dialogue_state.pending_followup,
            process_state_signals=ProcessStateSignals(),
        )


class StubRecommendationStateService:
    def sync_dialogue_state(self, **kwargs):
        dialogue_state = kwargs["dialogue_state"]
        dialogue_state.recommendation_ready = True
        return ReadinessStateUpdate(
            dialogue_state=dialogue_state,
            assessment_readiness=AssessmentReadiness(
                ready=True,
                has_medical_problem=True,
                reason_tags=["minimum_information_present"],
            ),
            pending_followup=dialogue_state.pending_followup,
        )


class StubSafetyManager:
    def assess_raw_message(self, turn_input):
        return SafetyState()

    def assess_extraction(self, extraction_payload):
        return SafetyState()

    def assess_case(self, medical_case):
        return SafetyState()


class StubConfirmationManager:
    def evaluate(self, context):
        return ConfirmationDecision(
            should_request_confirmation=False,
            trace_notes=["confirmation_placeholder"],
        )


class Block6ResponseTransitionTest(unittest.TestCase):
    def test_entry_manager_treats_no_as_dialogue_transition_resolution(self):
        classifier = TrackingIntentClassificationService()
        transition_service = FixedRecommendationTransitionService(
            RecommendationTransitionResolution(
                action="request_recommendation",
                trace_notes=["transition_resolution:test_request_recommendation"],
            )
        )
        entry_manager = EntryManager(
            intent_classification=classifier,
            recommendation_transition_service=transition_service,
        )
        context = types.SimpleNamespace(
            dialogue_state=DialogueState(
                pending_dialogue_transition=PendingDialogueTransition(
                    kind="recommendation_ready_check",
                    prompt_code="guide_next_step",
                )
            )
        )

        decision = entry_manager.evaluate(
            TurnInput(
                message="Nein.",
                session_id="test-session",
                conversation_messages=[],
            ),
            context=context,
        )

        self.assertFalse(classifier.called)
        self.assertTrue(transition_service.called)
        self.assertFalse(decision.extraction_required)
        self.assertTrue(decision.recommendation_requested)
        self.assertTrue(decision.clear_pending_dialogue_transition)
        self.assertEqual(decision.dialogue_transition_action, "request_recommendation")

    def test_entry_manager_derives_recommendation_transition_from_gateway_signals(self):
        transition_service = NullRecommendationTransitionService()
        gateway = IntentGateway(
            category="general_health_question",
            message_role="recommendation_request",
            profile="default",
            entry_signals=["medical_relevance:medical"],
            dispatch_signals=["next_step:response_only"],
            case_hints=[],
            dialogue_hints=["dialogue_hint:recommendation_requested"],
            safety_hints=[],
            trace_notes=["explicit recommendation request on transition node"],
        )
        classifier = FixedIntentClassificationService(gateway)
        entry_manager = EntryManager(
            intent_classification=classifier,
            recommendation_transition_service=transition_service,
        )
        context = types.SimpleNamespace(
            medical_case=MedicalCase(),
            pending_followup=None,
            dialogue_state=DialogueState(
                pending_dialogue_transition=PendingDialogueTransition(
                    kind="recommendation_ready_check",
                    prompt_code="guide_next_step",
                )
            ),
        )

        decision = entry_manager.evaluate(
            TurnInput(
                message="Bitte geben Sie mir jetzt die Empfehlung.",
                session_id="test-session",
                conversation_messages=[],
            ),
            context=context,
        )

        self.assertTrue(classifier.called)
        self.assertTrue(transition_service.called)
        self.assertFalse(decision.extraction_required)
        self.assertTrue(decision.recommendation_requested)
        self.assertTrue(decision.clear_pending_dialogue_transition)
        self.assertEqual(decision.dialogue_transition_action, "request_recommendation")
        self.assertIn(
            "dialogue_transition:recommendation_ready_check:request_recommendation",
            decision.trace_notes,
        )

    def test_entry_manager_keeps_medical_path_for_free_text_report_more_information(self):
        transition_service = FixedRecommendationTransitionService(
            RecommendationTransitionResolution(
                action="report_more_information",
                trace_notes=["transition_resolution:test_report_more_information"],
            )
        )
        gateway = IntentGateway(
            category="symptom_report",
            message_role="new_information",
            profile="default",
            entry_signals=["medical_relevance:medical"],
            dispatch_signals=[
                "next_step:extract",
                "operation_mode:focused_new_fact_extraction",
                "task:extract_symptoms",
            ],
            case_hints=["content_hint:symptom_present"],
            dialogue_hints=[],
            safety_hints=[],
            trace_notes=["new symptom after recommendation-ready check"],
        )
        classifier = FixedIntentClassificationService(gateway)
        entry_manager = EntryManager(
            intent_classification=classifier,
            recommendation_transition_service=transition_service,
        )
        context = types.SimpleNamespace(
            medical_case=MedicalCase(),
            pending_followup=None,
            dialogue_state=DialogueState(
                pending_dialogue_transition=PendingDialogueTransition(
                    kind="recommendation_ready_check",
                    prompt_code="guide_next_step",
                )
            ),
        )

        decision = entry_manager.evaluate(
            TurnInput(
                message="Ja, ich habe auch Fieber.",
                session_id="test-session",
                conversation_messages=[],
            ),
            context=context,
        )

        self.assertTrue(classifier.called)
        self.assertTrue(transition_service.called)
        self.assertTrue(decision.extraction_required)
        self.assertTrue(decision.clear_pending_dialogue_transition)
        self.assertEqual(decision.dialogue_transition_action, "report_more_information")
        self.assertIn(
            "transition_resolution:test_report_more_information",
            decision.trace_notes,
        )

    def test_entry_manager_uses_canonical_transition_action_for_return_to_medical_path(self):
        classifier = TrackingIntentClassificationService()
        transition_service = FixedRecommendationTransitionService(
            RecommendationTransitionResolution(
                action="report_more_information",
                trace_notes=["transition_resolution:test_report_more_information"],
            )
        )
        entry_manager = EntryManager(
            intent_classification=classifier,
            recommendation_transition_service=transition_service,
        )
        context = types.SimpleNamespace(
            dialogue_state=DialogueState(
                pending_dialogue_transition=PendingDialogueTransition(
                    kind="recommendation_ready_check",
                    prompt_code="guide_next_step",
                )
            )
        )

        decision = entry_manager.evaluate(
            TurnInput(
                message="report_more_information",
                session_id="test-session",
                conversation_messages=[],
            ),
            context=context,
        )

        self.assertFalse(classifier.called)
        self.assertTrue(transition_service.called)
        self.assertFalse(decision.extraction_required)
        self.assertFalse(decision.recommendation_requested)
        self.assertTrue(decision.clear_pending_dialogue_transition)
        self.assertEqual(decision.dialogue_transition_action, "report_more_information")
        self.assertIn(
            "transition_resolution:test_report_more_information",
            decision.trace_notes,
        )

    def test_entry_manager_keeps_transition_open_for_non_resolving_social_reply(self):
        transition_service = NullRecommendationTransitionService()
        gateway = IntentGateway(
            category="smalltalk",
            message_role="non_medical",
            profile="default",
            entry_signals=[
                "medical_relevance:non_medical",
                "social_mode:thanks",
            ],
            dispatch_signals=["next_step:response_only"],
            case_hints=[],
            dialogue_hints=["dialogue_hint:social_turn_without_medical_update"],
            safety_hints=[],
            trace_notes=["social acknowledgement on transition node"],
        )
        classifier = FixedIntentClassificationService(gateway)
        entry_manager = EntryManager(
            intent_classification=classifier,
            recommendation_transition_service=transition_service,
        )
        context = types.SimpleNamespace(
            medical_case=MedicalCase(),
            pending_followup=None,
            dialogue_state=DialogueState(
                recommendation_ready=True,
                pending_dialogue_transition=PendingDialogueTransition(
                    kind="recommendation_ready_check",
                    prompt_code="guide_next_step",
                )
            ),
        )

        decision = entry_manager.evaluate(
            TurnInput(
                message="Danke.",
                session_id="test-session",
                conversation_messages=[],
            ),
            context=context,
        )

        self.assertTrue(classifier.called)
        self.assertTrue(transition_service.called)
        self.assertFalse(decision.clear_pending_dialogue_transition)
        self.assertIsNone(decision.dialogue_transition_action)
        self.assertIsNone(decision.response_mode_hint)
        self.assertIn(
            "dialogue_transition:recommendation_ready_check:awaiting_resolved_reply",
            decision.trace_notes,
        )

    def test_dialogue_manager_turn_moves_from_guide_next_step_to_recommend(self):
        classifier = TrackingIntentClassificationService()
        transition_service = FixedRecommendationTransitionService(
            RecommendationTransitionResolution(
                action="request_recommendation",
                trace_notes=["transition_resolution:test_request_recommendation"],
            )
        )
        entry_manager = EntryManager(
            intent_classification=classifier,
            recommendation_transition_service=transition_service,
        )
        response_manager = ResponseManager()
        focus = CaseObservation(
            type="symptom",
            label="Husten",
            display_label="Husten",
            source_span="Husten",
            temporality="seit gestern",
        )
        existing_case = MedicalCase(
            observations=[focus],
            primary_problem_id=focus.id,
        )
        existing_state = DialogueState(
            recommendation_ready=True,
            pending_dialogue_transition=PendingDialogueTransition(
                kind="recommendation_ready_check",
                prompt_code="guide_next_step",
            ),
        )
        manager = DialogueManager(
            entry_manager=entry_manager,
            extraction_manager=StubExtractionManager(),
            case_state_manager=StubCaseStateManager(),
            safety_manager=StubSafetyManager(),
            response_manager=response_manager,
            confirmation_manager=StubConfirmationManager(),
            dialogue_state_service=StubDialogueStateService(),
            recommendation_state_service=StubRecommendationStateService(),
        )

        result = manager.run_turn(
            TurnInput(
                message="Nein.",
                session_id="test-session",
                conversation_messages=[
                    {
                        "role": "assistant",
                        "content": (
                            "Moechten Sie jetzt eine Versorgungsempfehlung "
                            "erhalten oder haben Sie noch weitere Beschwerden?"
                        ),
                    }
                ],
                existing_case=existing_case,
                existing_dialogue_state=existing_state,
            )
        )

        self.assertFalse(classifier.called)
        self.assertTrue(transition_service.called)
        self.assertEqual(result.response_mode, "recommend")
        self.assertEqual(
            result.context.response_state.recommendation_state,
            "ready_for_recommendation",
        )
        self.assertEqual(
            result.context.response_state.transition_state,
            "commit_recommendation",
        )
        self.assertTrue(result.context.dialogue_state.recommendation_requested)
        self.assertTrue(result.context.dialogue_state.recommendation_ready)
        self.assertIsNone(result.context.dialogue_state.pending_dialogue_transition)

    def test_dialogue_manager_repeats_transition_for_non_resolving_social_reply(self):
        transition_service = NullRecommendationTransitionService()
        gateway = IntentGateway(
            category="smalltalk",
            message_role="non_medical",
            profile="default",
            entry_signals=[
                "medical_relevance:non_medical",
                "social_mode:thanks",
            ],
            dispatch_signals=["next_step:response_only"],
            case_hints=[],
            dialogue_hints=["dialogue_hint:social_turn_without_medical_update"],
            safety_hints=[],
            trace_notes=["social acknowledgement on transition node"],
        )
        classifier = FixedIntentClassificationService(gateway)
        entry_manager = EntryManager(
            intent_classification=classifier,
            recommendation_transition_service=transition_service,
        )
        response_manager = ResponseManager()
        focus = CaseObservation(
            type="symptom",
            label="Husten",
            display_label="Husten",
            source_span="Husten",
            temporality="seit gestern",
        )
        existing_case = MedicalCase(
            observations=[focus],
            primary_problem_id=focus.id,
        )
        existing_state = DialogueState(
            recommendation_ready=True,
            pending_dialogue_transition=PendingDialogueTransition(
                kind="recommendation_ready_check",
                prompt_code="guide_next_step",
            ),
        )
        manager = DialogueManager(
            entry_manager=entry_manager,
            extraction_manager=StubExtractionManager(),
            case_state_manager=StubCaseStateManager(),
            safety_manager=StubSafetyManager(),
            response_manager=response_manager,
            confirmation_manager=StubConfirmationManager(),
            dialogue_state_service=StubDialogueStateService(),
            recommendation_state_service=StubRecommendationStateService(),
        )

        result = manager.run_turn(
            TurnInput(
                message="Danke.",
                session_id="test-session",
                conversation_messages=[
                    {
                        "role": "assistant",
                        "content": (
                            "Moechten Sie jetzt eine Versorgungsempfehlung "
                            "erhalten oder haben Sie noch weitere Beschwerden?"
                        ),
                    }
                ],
                existing_case=existing_case,
                existing_dialogue_state=existing_state,
            )
        )

        self.assertTrue(classifier.called)
        self.assertTrue(transition_service.called)
        self.assertEqual(result.response_mode, "guide_next_step")
        self.assertEqual(
            result.context.response_state.recommendation_state,
            "ready_for_transition",
        )
        self.assertEqual(
            result.context.response_state.transition_state,
            "awaiting_reply",
        )
        self.assertEqual(
            result.response_text,
            "Moechten Sie jetzt eine Versorgungsempfehlung erhalten oder haben Sie noch weitere Beschwerden?",
        )
        self.assertIsNotNone(result.context.dialogue_state.pending_dialogue_transition)
        self.assertEqual(
            result.context.dialogue_state.pending_dialogue_transition.kind,
            "recommendation_ready_check",
        )

    def test_dialogue_manager_moves_from_transition_to_medical_path_on_canonical_action(self):
        classifier = TrackingIntentClassificationService()
        transition_service = FixedRecommendationTransitionService(
            RecommendationTransitionResolution(
                action="report_more_information",
                trace_notes=["transition_resolution:test_report_more_information"],
            )
        )
        entry_manager = EntryManager(
            intent_classification=classifier,
            recommendation_transition_service=transition_service,
        )
        response_manager = ResponseManager()
        focus = CaseObservation(
            type="symptom",
            label="Husten",
            display_label="Husten",
            source_span="Husten",
            temporality="seit gestern",
        )
        existing_case = MedicalCase(
            observations=[focus],
            primary_problem_id=focus.id,
        )
        existing_state = DialogueState(
            recommendation_ready=True,
            pending_dialogue_transition=PendingDialogueTransition(
                kind="recommendation_ready_check",
                prompt_code="guide_next_step",
            ),
        )
        manager = DialogueManager(
            entry_manager=entry_manager,
            extraction_manager=StubExtractionManager(),
            case_state_manager=StubCaseStateManager(),
            safety_manager=StubSafetyManager(),
            response_manager=response_manager,
            confirmation_manager=StubConfirmationManager(),
            dialogue_state_service=StubDialogueStateService(),
            recommendation_state_service=StubRecommendationStateService(),
        )

        result = manager.run_turn(
            TurnInput(
                message="report_more_information",
                session_id="test-session",
                conversation_messages=[
                    {
                        "role": "assistant",
                        "content": (
                            "Moechten Sie jetzt eine Versorgungsempfehlung "
                            "erhalten oder haben Sie noch weitere Beschwerden?"
                        ),
                    }
                ],
                existing_case=existing_case,
                existing_dialogue_state=existing_state,
            )
        )

        self.assertFalse(classifier.called)
        self.assertTrue(transition_service.called)
        self.assertEqual(result.response_mode, "continue")
        self.assertEqual(
            result.context.response_state.transition_state,
            "return_to_medical",
        )
        self.assertEqual(
            result.response_text,
            "Okay, dann beschreiben Sie bitte kurz die weiteren Beschwerden.",
        )
        self.assertIsNone(result.context.dialogue_state.pending_dialogue_transition)


if __name__ == "__main__":
    unittest.main()
