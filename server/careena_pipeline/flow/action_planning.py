from careena_pipeline.llm.next_step_advisor import LLMNextStepAdvisor
from careena_pipeline.observability import log_json
from careena_pipeline.planning import AssessmentReadinessEvaluator
from careena_pipeline.planning.recommendation_gate import RecommendationGate
from careena_pipeline.state import DialogueStateManager
from careena_pipeline.models import (
    DialogueState,
    MedicalCase,
    MessageUpdate,
    SafetyResult,
)
from careena_pipeline.flow.outcomes import ActionPlanningOutcome


class ActionPlanningStep:
    """Orchestrates readiness evaluation and next-step decisioning."""

    def __init__(
        self,
        *,
        readiness: AssessmentReadinessEvaluator,
        dialogue_state_manager: DialogueStateManager,
        recommendation_gate: RecommendationGate,
        next_step_advisor: LLMNextStepAdvisor | None = None,
    ):
        self.readiness = readiness
        self.dialogue_state_manager = dialogue_state_manager
        self.recommendation_gate = recommendation_gate
        self.next_step_advisor = next_step_advisor

    def plan(
        self,
        *,
        text: str,
        case: MedicalCase,
        dialogue_state: DialogueState,
        message_update: MessageUpdate | None,
        safety: SafetyResult,
        request_recommendation: bool = False,
        force_deterministic_gate: bool = False,
    ) -> ActionPlanningOutcome:
        readiness = self.readiness.evaluate(
            case,
            dialogue_state=dialogue_state,
            message_update=message_update,
        )
        case.ensure_primary_problem()
        log_json("ASSESSMENT READINESS", readiness)

        gate = self._decide_next_step(
            case=case,
            dialogue_state=dialogue_state,
            message_update=message_update,
            safety=safety,
            readiness=readiness,
            last_user_message=text,
            request_recommendation=request_recommendation,
            force_deterministic_gate=force_deterministic_gate,
        )
        log_json("RECOMMENDATION GATE", gate)

        dialogue_state = self.dialogue_state_manager.apply_planning_outcome(
            dialogue_state,
            readiness=readiness,
            gate=gate,
            case=case,
        )
        self.dialogue_state_manager.sync_case(case, dialogue_state)
        return ActionPlanningOutcome(
            dialogue_state=dialogue_state,
            readiness=readiness,
            gate=gate,
        )

    def _decide_next_step(
        self,
        *,
        case: MedicalCase,
        dialogue_state: DialogueState,
        message_update: MessageUpdate | None,
        safety: SafetyResult,
        readiness,
        last_user_message: str,
        request_recommendation: bool = False,
        force_deterministic_gate: bool = False,
    ):
        if force_deterministic_gate or self.next_step_advisor is None:
            return self.recommendation_gate.decide(
                readiness=readiness,
                user_requests_recommendation=request_recommendation,
            )

        if readiness.blocking_requirements and message_update is None:
            return self.recommendation_gate.decide(
                readiness=readiness,
                user_requests_recommendation=request_recommendation,
            )

        return self.next_step_advisor.decide(
            case=case,
            dialogue_state=dialogue_state,
            message_update=message_update,
            safety=safety,
            readiness=readiness,
            last_user_message=last_user_message,
            user_requests_recommendation=request_recommendation,
        )
