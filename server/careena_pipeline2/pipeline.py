from __future__ import annotations

import logging

from careena_pipeline2.medical_context import MedicalContextGate
from careena_pipeline2.core.exceptions import ExtractionError
from careena_pipeline2.llm import MessageExtractor
from careena_pipeline2.logs import log_json, log_pipeline_outcome
from careena_pipeline2.models import (
    AssessmentReadiness,
    DialogueState,
    MedicalCase,
    MessageUpdate,
    PipelineResult,
    Recommendation,
    SafetyResult,
    MedicalContextStatus,
    RedFlagStatus,
)
from careena_pipeline2.planning import DecisionPlanner
from careena_pipeline2.routing import RecommendationRouter
from careena_pipeline2.safety import SafetyDecisionMerger, SafetyGate
from careena_pipeline2.state import CaseUpdater, ConfirmationService
from careena_pipeline2.text import (
    is_affirmative_confirmation,
    is_negative_confirmation,
    question_for_requirement,
)


logger = logging.getLogger(__name__)


class CareenaConversationPipeline:
    def __init__(
        self,
        message_extractor: MessageExtractor,
        *,
        safety_gate: SafetyGate | None = None,
        case_updater: CaseUpdater | None = None,
        confirmation_service: ConfirmationService | None = None,
        planner: DecisionPlanner | None = None,
        router: RecommendationRouter | None = None,
    ):
        self.message_extractor = message_extractor
        self.safety_gate = safety_gate or SafetyGate()
        self.medical_context_gate = MedicalContextGate()
        self.safety_decision_merger = SafetyDecisionMerger()
        self.case_updater = case_updater or CaseUpdater()
        self.confirmation_service = confirmation_service or ConfirmationService()
        self.planner = planner or DecisionPlanner()
        self.router = router or RecommendationRouter()

    def run(
        self,
        text: str,
        existing_case: MedicalCase | None = None,
        existing_dialogue_state: DialogueState | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> PipelineResult:
        log_json(
            "PIPELINE INPUT",
            {
                "text": text,
                "has_existing_case": existing_case is not None,
                "has_existing_dialogue_state": existing_dialogue_state is not None,
                "conversation_turns": len(conversation_messages or []),
            },
        )
        case = existing_case.model_copy(deep=True) if existing_case is not None else MedicalCase()
        dialogue_state = (
            existing_dialogue_state.model_copy(deep=True)
            if existing_dialogue_state is not None
            else DialogueState()
        )
        case.ensure_primary_problem()
        if dialogue_state.focus_observation_id is None:
            dialogue_state.focus_observation_id = case.primary_problem_id

        raw_context = self.medical_context_gate.evaluate_raw_text(text)
        raw_safety = self.safety_gate.evaluate_raw_text(text)
        raw_red_flag_status = self.safety_decision_merger.merge(
            raw_result=raw_safety,
            structured_result=None,
        )

    

        if dialogue_state.awaiting_confirmation and is_affirmative_confirmation(text):
            self.confirmation_service.confirm_pending(case, dialogue_state)
            return self._finalize(
                self._plan_and_finalize(
                    text=text,
                    case=case,
                    dialogue_state=dialogue_state,
                    message_update=None,
                    raw_safety=raw_safety,
                    raw_context=raw_context,
                )
            )

        if dialogue_state.awaiting_confirmation and is_negative_confirmation(text):
            self.confirmation_service.clear_pending(dialogue_state)
            readiness = AssessmentReadiness(
                ready=False,
                missing_requirements=[],
                reason_tags=["confirmation_rejected"],
            )
            return self._finalize(
                self._result(
                    text=text,
                    safety=raw_safety,
                    case=case,
                    dialogue_state=dialogue_state,
                    readiness=readiness,
                    response_mode="ask_followup",
                    followup_question="Was soll ich korrigieren oder ergaenzen?",
                )
            )

        try:
            message_update = self.message_extractor.extract_update(
                text=text,
                existing_case=case,
                dialogue_state=dialogue_state,
                conversation_messages=conversation_messages,
            )
        except ExtractionError as exc:
            logger.warning("Message extraction failed: %s", exc)
                        # If raw safety found a possible red flag, the extraction error must
            # not fall back to the normal "cannot assess" response.
            if raw_red_flag_status.requires_safety_question:
                return self._finalize(
                    self._result(
                        text=text,
                        safety=raw_safety,
                        medical_context=raw_context,
                        red_flag_status=raw_red_flag_status,
                        case=case,
                        dialogue_state=dialogue_state,
                        response_mode="safety_clarification",
                        followup_question=raw_red_flag_status.safety_question,
                    )
                )
            followup_question = None
            response_mode = "cannot_assess"
            if dialogue_state.pending_requirement:
                followup_question = question_for_requirement(dialogue_state.pending_requirement)
                response_mode = "ask_followup"
            else:
                followup_question = (
                    "Bitte beschreiben Sie die gesundheitliche Beschwerde noch einmal moeglichst konkret."
                )
            return self._finalize(
                self._result(
                    text=text,
                    safety=raw_safety,
                    medical_context=raw_context,
                    red_flag_status=raw_red_flag_status,
                    case=case,
                    dialogue_state=dialogue_state,
                    response_mode=response_mode,
                    followup_question=followup_question,
                )
            )

        if (
            not message_update.is_medical
            and not message_update.user_requests_recommendation
            and not message_update.observations
            and message_update.subject is None
            and not raw_safety.red_flag_detected
        ):
            response_mode = (
                "out_of_scope"
                if message_update.intent_category in {"smalltalk", "not_medical"}
                else "cannot_assess"
            )
            return self._finalize(
                self._result(
                    text=text,
                    safety=raw_safety,
                    medical_context=raw_context,
                    red_flag_status=raw_red_flag_status,
                    case=case,
                    dialogue_state=dialogue_state,
                    message_update=message_update,
                    response_mode=response_mode,
                )
            )

        dialogue_state.recommendation_requested = (
            dialogue_state.recommendation_requested
            or message_update.user_requests_recommendation
            or message_update.message_role == "recommendation_request"
        )

        merge_result = self.case_updater.apply(case, dialogue_state, message_update)
        case = merge_result.case
        dialogue_state = merge_result.dialogue_state

        if dialogue_state.awaiting_confirmation:
            if message_update.message_role == "confirmation":
                self.confirmation_service.confirm_pending(case, dialogue_state)
            elif message_update.message_role == "correction":
                self.confirmation_service.clear_pending(dialogue_state)

        return self._finalize(
            self._plan_and_finalize(
                text=text,
                case=case,
                dialogue_state=dialogue_state,
                message_update=message_update,
                raw_safety=raw_safety,
                raw_context=raw_context,
            )
        )

    def _plan_and_finalize(
        self,
        *,
        text: str,
        case: MedicalCase,
        dialogue_state: DialogueState,
        message_update: MessageUpdate | None,
        raw_safety: SafetyResult,
        raw_context: MedicalContextStatus,
    ) -> PipelineResult:
        structured_context = self.medical_context_gate.evaluate_structured_case(case)
        medical_context = self._merge_medical_context(raw_context, structured_context)

        structured_safety = self.safety_gate.evaluate_structured_case(case)
        red_flag_status = self.safety_decision_merger.merge(
            raw_result=raw_safety,
            structured_result=structured_safety,
        )

        if red_flag_status.red_flag:
            final_safety = structured_safety if structured_safety.red_flag_detected else raw_safety

            return self._result(
                text=text,
                safety=final_safety,
                medical_context=medical_context,
                red_flag_status=red_flag_status,
                case=case,
                dialogue_state=dialogue_state,
                message_update=message_update,
                response_mode="emergency",
            )

        if red_flag_status.requires_safety_question:
            dialogue_state.last_assistant_question = red_flag_status.safety_question

            readiness = AssessmentReadiness(
                ready=False,
                missing_requirements=["red_flag_clarification"],
                reason_tags=["red_flag_clarification_required"],
            )

            return self._result(
                text=text,
                safety=raw_safety,
                medical_context=medical_context,
                red_flag_status=red_flag_status,
                case=case,
                dialogue_state=dialogue_state,
                message_update=message_update,
                readiness=readiness,
                response_mode="safety_clarification",
                followup_question=red_flag_status.safety_question,
            )

        decision = self.planner.decide(case, dialogue_state)

        if decision.action == "ask_followup":
            dialogue_state.last_assistant_question = decision.question

            return self._result(
                text=text,
                safety=structured_safety,
                medical_context=medical_context,
                red_flag_status=red_flag_status,
                case=case,
                dialogue_state=dialogue_state,
                message_update=message_update,
                readiness=decision.readiness,
                response_mode="ask_followup",
                followup_question=decision.question,
            )

        if decision.action == "confirm_case":
            dialogue_state.last_assistant_question = "Stimmt das so?"

            return self._result(
                text=text,
                safety=structured_safety,
                medical_context=medical_context,
                red_flag_status=red_flag_status,
                case=case,
                dialogue_state=dialogue_state,
                message_update=message_update,
                readiness=decision.readiness,
                response_mode="confirm_case",
            )

        confirmed_case = case.clone_confirmed_case()
        recommendation = self.router.recommend(confirmed_case)
        dialogue_state.last_assistant_question = None

        return self._result(
            text=text,
            safety=structured_safety,
            medical_context=medical_context,
            red_flag_status=red_flag_status,
            case=case,
            dialogue_state=dialogue_state,
            message_update=message_update,
            readiness=decision.readiness,
            recommendation=recommendation,
            response_mode="recommend",
        )

    @staticmethod
    def _merge_medical_context(
        raw_context: MedicalContextStatus,
        structured_context: MedicalContextStatus,
    ) -> MedicalContextStatus:
        """Merge raw and structured medical context checks into one result."""
        final_status = structured_context.final_status

        if raw_context.final_status == "smalltalk" and structured_context.final_status == "unclear":
            final_status = "smalltalk"

        if raw_context.final_status == "out_of_scope" and structured_context.final_status == "unclear":
            final_status = "out_of_scope"

        if structured_context.final_status == "in_scope":
            final_status = "in_scope"

        merged = structured_context.model_copy(deep=True)
        merged.raw_status = raw_context.raw_status
        merged.final_status = final_status
        merged.reason_tags = list(
            dict.fromkeys(raw_context.reason_tags + structured_context.reason_tags)
        )
        merged.confidence = max(raw_context.confidence, structured_context.confidence)

        return merged

    @staticmethod
    def _result(
        *,
        text: str,
        safety: SafetyResult,
        response_mode: str,
        medical_context: MedicalContextStatus | None = None,
        red_flag_status: RedFlagStatus | None = None,
        case: MedicalCase | None = None,
        dialogue_state: DialogueState | None = None,
        message_update: MessageUpdate | None = None,
        readiness: AssessmentReadiness | None = None,
        recommendation: Recommendation | None = None,
        followup_question: str | None = None,
    ) -> PipelineResult:
        return PipelineResult(
            raw_text=text,
            safety=safety,
            medical_context=medical_context,
            red_flag_status=red_flag_status,
            case=case,
            dialogue_state=dialogue_state,
            message_update=message_update,
            readiness=readiness,
            recommendation=recommendation,
            response_mode=response_mode,
            followup_question=followup_question,
        )

    @staticmethod
    def _finalize(result: PipelineResult) -> PipelineResult:
        log_pipeline_outcome(result)
        return result
