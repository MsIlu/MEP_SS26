import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena_pipeline3.application.managers.response_manager import ResponseManager
from careena_pipeline3.application.services.response_generation_service import (
    ResponseGenerationService,
)
from careena_pipeline3.models.domain import DialogueState, PendingFollowup
from careena_pipeline3.models.turn import (
    EntryDecision,
    ProcessStateSignals,
    RecommendationGateDecision,
    ResolvedFollowup,
    SafetyState,
    TurnContext,
)
from careena_pipeline3.models.workflow import AssessmentReadiness


def test_followup_slot_update_uses_static_acknowledgement():
    manager = ResponseManager()
    context = _build_context()
    context.process_state_signals = ProcessStateSignals(
        resolved_followup=ResolvedFollowup(
            requirement_key="symptom.duration_or_onset",
            slot="duration_or_onset",
            focus_label="schlecht Luft bekommen",
        )
    )

    plan = manager.plan(
        context=context,
        entry_decision=EntryDecision(call2_operation_mode="followup_slot_update"),
        raw_safety=SafetyState(),
        extraction_safety=SafetyState(),
        case_safety=SafetyState(),
    )

    assert plan.response_mode == "continue"
    assert plan.response_strategy.kind == "static_followup_resolution_ack"
    assert "?" not in (plan.response_text or "")


def test_mixed_followup_resolution_keeps_llm_continue_path():
    llm = _RecordingLLMResponseGeneration()
    manager = ResponseManager(
        response_generation_service=_ResponseGenerationWithLLM(llm)
    )
    context = _build_context()
    context.process_state_signals = ProcessStateSignals(
        resolved_followup=ResolvedFollowup(
            requirement_key="symptom.duration_or_onset",
            slot="duration_or_onset",
            focus_label="schlecht Luft bekommen",
        ),
        additional_medical_information_detected=True,
    )

    plan = manager.plan(
        context=context,
        entry_decision=EntryDecision(call2_operation_mode="mixed_update_and_new_info"),
        raw_safety=SafetyState(),
        extraction_safety=SafetyState(),
        case_safety=SafetyState(),
        latest_user_message="seit ein paar tagen und jetzt auch Husten",
    )

    assert plan.response_strategy.kind == "llm_followup_resolved_continue"
    assert plan.response_text == "Kurze Weiterfuehrung ohne Wiederholung."
    assert llm.last_prompt is not None
    assert "Resolved Follow-up This Turn: true" in llm.last_prompt
    assert "Additional Medical Information Detected: true" in llm.last_prompt


def test_open_pending_followup_still_asks_followup():
    manager = ResponseManager()
    context = _build_context()
    context.dialogue_state = DialogueState(
        pending_followup=PendingFollowup(
            requirement_key="symptom.duration_or_onset",
            slot="duration_or_onset",
            kind="requirement",
            focus_label="schlecht Luft bekommen",
        )
    )
    context.gate_decision = RecommendationGateDecision(
        gate_status="concern_clarification",
        allowed_next_step="ask_clarifying_question",
        reason_tags=[],
    )
    context.process_state_signals = ProcessStateSignals()

    plan = manager.plan(
        context=context,
        entry_decision=EntryDecision(call2_operation_mode="focused_new_fact_extraction"),
        raw_safety=SafetyState(),
        extraction_safety=SafetyState(),
        case_safety=SafetyState(),
    )

    assert plan.response_mode == "ask_followup"
    assert plan.response_strategy.kind == "static_followup"


def _build_context() -> TurnContext:
    return TurnContext(
        dialogue_state=DialogueState(),
        assessment_readiness=AssessmentReadiness(
            ready=True,
            has_medical_problem=True,
            reason_tags=["minimum_information_present"],
        ),
        gate_decision=RecommendationGateDecision(
            gate_status="medical_exploration",
            allowed_next_step="continue_medical",
            reason_tags=["gate:concern_phase:exploration"],
        ),
    )


class _RecordingLLMResponseGeneration:
    def __init__(self) -> None:
        self.last_prompt: str | None = None

    def build(self, **kwargs) -> str:
        context = kwargs["context"]
        response_state = kwargs["response_state"]
        response_strategy = kwargs["response_strategy"]
        entry_decision = kwargs["entry_decision"]
        latest_user_message = kwargs["latest_user_message"]
        from careena_pipeline3.application.services.llm_response_generation_service import (
            _build_user_prompt,
        )

        self.last_prompt = _build_user_prompt(
            response_mode=kwargs["response_mode"],
            response_state=response_state,
            response_strategy=response_strategy,
            context=context,
            entry_decision=entry_decision,
            latest_user_message=latest_user_message,
            response_history_messages=kwargs.get("response_history_messages"),
        )
        return "Kurze Weiterfuehrung ohne Wiederholung."


class _ResponseGenerationWithLLM:
    def __init__(self, llm) -> None:
        self._service = ResponseGenerationService(llm_response_generation=llm)

    def build(self, **kwargs) -> str:
        return self._service.build(**kwargs)
