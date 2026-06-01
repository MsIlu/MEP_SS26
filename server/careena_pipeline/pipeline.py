from careena_pipeline.llm import (
    LLMCaseUpdateExtractor,
    LLMNextStepAdvisor,
    LLMRoutingAdvisor,
)
from careena_pipeline.observability import log_json, log_pipeline_outcome
from careena_pipeline.planning import (
    AssessmentReadinessEvaluator,
    SlotFiller,
)
from careena_pipeline.models import CareenaPipelineResult, DialogueState, MedicalCase
from careena_pipeline.planning.recommendation_gate import RecommendationGate
from careena_pipeline.routing.fallback_engine import RecommendationEngine
from careena_pipeline.safety import SafetyGate
from careena_pipeline.state import CaseMerger, DialogueStateManager
from careena_pipeline.flow import (
    ActionPlanningStep,
    MessageParsingStep,
    RecommendationStep,
    StructuredSafetyStep,
)


class CareenaDecisionPipeline:
    """
    Coordinates the decision pipeline through explicit application steps.

    The compatibility surface stays stable while the internal flow is split
    into parse, safety, planning, and recommendation stages.
    """

    def __init__(
        self,
        case_update_extractor: LLMCaseUpdateExtractor,
        safety_gate: SafetyGate | None = None,
        case_merger: CaseMerger | None = None,
        slot_filler: SlotFiller | None = None,
        dialogue_state_manager: DialogueStateManager | None = None,
        readiness: AssessmentReadinessEvaluator | None = None,
        recommendation_gate: RecommendationGate | None = None,
        recommendation_engine: RecommendationEngine | None = None,
        next_step_advisor: LLMNextStepAdvisor | None = None,
        routing_advisor: LLMRoutingAdvisor | None = None,
    ):
        safety_gate = safety_gate or SafetyGate()
        case_merger = case_merger or CaseMerger()
        slot_filler = slot_filler or SlotFiller()
        dialogue_state_manager = dialogue_state_manager or DialogueStateManager()
        readiness = readiness or AssessmentReadinessEvaluator()
        recommendation_gate = recommendation_gate or RecommendationGate()
        recommendation_engine = recommendation_engine or RecommendationEngine()

        self.message_parsing = MessageParsingStep(
            case_update_extractor=case_update_extractor,
            safety_gate=safety_gate,
            case_merger=case_merger,
            slot_filler=slot_filler,
            dialogue_state_manager=dialogue_state_manager,
        )
        self.structured_safety = StructuredSafetyStep(safety_gate)
        self.action_planning = ActionPlanningStep(
            readiness=readiness,
            dialogue_state_manager=dialogue_state_manager,
            recommendation_gate=recommendation_gate,
            next_step_advisor=next_step_advisor,
        )
        self.recommendation_step = RecommendationStep(
            recommendation_engine=recommendation_engine,
            routing_advisor=routing_advisor,
        )

    def run(
        self,
        text: str,
        existing_case: MedicalCase | None = None,
        existing_dialogue_state: DialogueState | None = None,
        pending_slot: str | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> CareenaPipelineResult:
        log_json("PIPELINE INPUT", {"text": text})

        parse_outcome = self.message_parsing.parse(
            text=text,
            existing_case=existing_case,
            existing_dialogue_state=existing_dialogue_state,
            pending_slot=pending_slot,
            conversation_messages=conversation_messages,
        )

        if parse_outcome.early_response_mode is not None:
            return self._finalize_result(
                text=text,
                safety=parse_outcome.raw_safety,
                case=parse_outcome.case,
                dialogue_state=parse_outcome.dialogue_state,
                message_update=parse_outcome.message_update,
                response_mode=parse_outcome.early_response_mode,
            )

        case = parse_outcome.case
        if case is None:
            return self._finalize_result(
                text=text,
                safety=parse_outcome.raw_safety,
                dialogue_state=parse_outcome.dialogue_state,
                message_update=parse_outcome.message_update,
                response_mode="cannot_assess",
            )

        structured_safety = self.structured_safety.assess(text=text, case=case)
        if structured_safety.red_flag_detected:
            return self._finalize_result(
                text=text,
                safety=structured_safety,
                case=case,
                dialogue_state=parse_outcome.dialogue_state,
                message_update=parse_outcome.message_update,
                response_mode="emergency",
            )

        planning_outcome = self.action_planning.plan(
            text=text,
            case=case,
            dialogue_state=parse_outcome.dialogue_state,
            message_update=parse_outcome.message_update,
            safety=structured_safety,
            request_recommendation=parse_outcome.request_recommendation,
            force_deterministic_gate=parse_outcome.force_deterministic_gate,
        )

        if planning_outcome.gate.action == "ask_followup":
            return self._finalize_result(
                text=text,
                safety=structured_safety,
                case=case,
                dialogue_state=planning_outcome.dialogue_state,
                message_update=parse_outcome.message_update,
                readiness=planning_outcome.readiness,
                recommendation_gate=planning_outcome.gate,
                response_mode="ask_followup",
            )

        if planning_outcome.gate.action == "confirm_information":
            return self._finalize_result(
                text=text,
                safety=structured_safety,
                case=case,
                dialogue_state=planning_outcome.dialogue_state,
                message_update=parse_outcome.message_update,
                readiness=planning_outcome.readiness,
                recommendation_gate=planning_outcome.gate,
                response_mode="confirm_information",
            )

        recommendation = self.recommendation_step.recommend(
            case=case,
            safety=structured_safety,
            gate=planning_outcome.gate,
        )
        log_json("RECOMMENDATION", recommendation)

        return self._finalize_result(
            text=text,
            safety=structured_safety,
            case=case,
            dialogue_state=planning_outcome.dialogue_state,
            message_update=parse_outcome.message_update,
            readiness=planning_outcome.readiness,
            recommendation_gate=planning_outcome.gate,
            recommendation=recommendation,
            response_mode="recommend",
        )

    @staticmethod
    def _finalize_result(
        *,
        text: str,
        safety,
        response_mode: str,
        case: MedicalCase | None = None,
        dialogue_state: DialogueState | None = None,
        message_update=None,
        readiness=None,
        recommendation_gate=None,
        recommendation=None,
    ) -> CareenaPipelineResult:
        result = CareenaPipelineResult(
            raw_text=text,
            safety=safety,
            case=case,
            dialogue_state=dialogue_state,
            message_update=message_update,
            readiness=readiness,
            recommendation_gate=recommendation_gate,
            recommendation=recommendation,
            response_mode=response_mode,
        )
        log_pipeline_outcome(result)
        return result
