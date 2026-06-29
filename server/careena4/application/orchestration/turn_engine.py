from careena4.application.dialogue.question_builder import QuestionBuilder
from careena4.application.dialogue.question_resolver import QuestionResolver
from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.application.dialogue.safety_clarification_builder import SafetyClarificationBuilder
from careena4.application.entry.entry_classifier import EntryClassifier
from careena4.application.extraction.medical_extractor import MedicalExtractor
from careena4.application.input import SymptomChipBuilder
from careena4.application.input import UnderstandingSymptomDraftAdapter
from careena4.application.recommendation.recommendation_builder import RecommendationBuilder
from careena4.application.response.response_builder import ResponseBuilder
from careena4.application.response.response_policy import ResponsePolicy
from careena4.application.safety import CaseSafetyEvaluator
from careena4.application.topic import TopicUpdater
from careena4.application.understanding import MedGemmaTurnUnderstandingService
from careena4.domain.case import CaseManager
from careena4.domain.quality.followup_need_builder import FollowupNeedBuilder
from careena4.domain.quality.followup_selector import FollowupSelector
from careena4.domain.readiness.readiness_evaluator import AssessmentReadinessBuilder, ReadinessEvaluator
from careena4.models.domain import ActiveQuestion, ConversationState, MedicalCase, RecommendationState
from careena4.models.turn import RecommendationRequestInput, TurnDecision, TurnInput, TurnResult
from careena4.server_log import log_event


class TurnEngine:
    def __init__(
        self,
        *,
        raw_red_flag_detector: RawRedFlagDetector | None = None,
        safety_clarification_builder: SafetyClarificationBuilder | None = None,
        entry_classifier: EntryClassifier | None = None,
        question_resolver: QuestionResolver | None = None,
        topic_updater: TopicUpdater | None = None,
        medical_extractor: MedicalExtractor | None = None,
        case_manager: CaseManager | None = None,
        followup_need_builder: FollowupNeedBuilder | None = None,
        followup_selector: FollowupSelector | None = None,
        question_builder: QuestionBuilder | None = None,
        readiness_evaluator: ReadinessEvaluator | None = None,
        readiness_builder: AssessmentReadinessBuilder | None = None,
        recommendation_builder: RecommendationBuilder | None = None,
        response_policy: ResponsePolicy | None = None,
        response_builder: ResponseBuilder | None = None,
        turn_understanding_service: MedGemmaTurnUnderstandingService | None = None,
        understanding_symptom_draft_adapter: UnderstandingSymptomDraftAdapter | None = None,
        case_safety_evaluator: CaseSafetyEvaluator | None = None,
    ):
        self.raw_red_flag_detector = raw_red_flag_detector or RawRedFlagDetector()
        self.safety_clarification_builder = safety_clarification_builder or SafetyClarificationBuilder()
        self.case_manager = case_manager or CaseManager()
        self.entry_classifier = entry_classifier or EntryClassifier(case_manager=self.case_manager)
        self.question_resolver = question_resolver or QuestionResolver()
        self.topic_updater = topic_updater or TopicUpdater(case_manager=self.case_manager)
        self.medical_extractor = medical_extractor or MedicalExtractor()
        self.symptom_chip_builder = SymptomChipBuilder()
        self.followup_need_builder = followup_need_builder or FollowupNeedBuilder(case_manager=self.case_manager)
        self.followup_selector = followup_selector or FollowupSelector()
        self.question_builder = question_builder or QuestionBuilder()
        self.readiness_evaluator = readiness_evaluator or ReadinessEvaluator(case_manager=self.case_manager)
        self.readiness_builder = readiness_builder or AssessmentReadinessBuilder(case_manager=self.case_manager)
        self.recommendation_builder = recommendation_builder or RecommendationBuilder(case_manager=self.case_manager)
        self.response_policy = response_policy or ResponsePolicy()
        self.response_builder = response_builder or ResponseBuilder(case_manager=self.case_manager)
        self.turn_understanding_service = turn_understanding_service
        self.understanding_symptom_draft_adapter = (
            understanding_symptom_draft_adapter or UnderstandingSymptomDraftAdapter()
        )
        self.case_safety_evaluator = case_safety_evaluator or CaseSafetyEvaluator()

    def run_turn(self, turn_input: TurnInput) -> TurnResult:
        medical_case = turn_input.persisted_medical_case or MedicalCase()
        conversation_state = turn_input.persisted_conversation_state or ConversationState()
        recommendation_state = turn_input.persisted_recommendation_state or RecommendationState()
        symptom_input_draft = turn_input.persisted_symptom_input_draft
        trace_notes: list[str] = []
        current_turn_understanding = None
        resolved_question: ActiveQuestion | None = None
        resolution_additional_information = False

        log_event(
            "turn.start",
            layer="application",
            session_id=turn_input.session_id,
            turn_id=turn_input.turn_id,
            has_topic=self.case_manager.has_topic(medical_case=medical_case),
            has_medical_case=turn_input.persisted_medical_case is not None,
            has_active_question=conversation_state.active_question is not None,
        )

        raw_safety = self.raw_red_flag_detector.detect(turn_input.message)
        trace_notes.extend(raw_safety.trace_notes)
        if raw_safety.requires_emergency_response:
            decision = TurnDecision(
                kind="ask_safety_question",
                response_mode="emergency",
                recommendation_ready=False,
                trace_notes=["turn:emergency_shortcut"],
            )
            return self._build_result(
                response_input=turn_input,
                decision=decision,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=current_turn_understanding,
                trace_notes=trace_notes,
            )

        if self.turn_understanding_service is not None:
            current_turn_understanding = self.turn_understanding_service.extract(
                message=turn_input.message,
            )
            trace_notes.extend(current_turn_understanding.trace_notes)
            symptom_input_draft = self.understanding_symptom_draft_adapter.update_from_understanding(
                draft=symptom_input_draft,
                understanding=current_turn_understanding,
                session_id=turn_input.session_id,
            )
            if current_turn_understanding.symptoms:
                trace_notes.append("symptom_input_draft:updated_from_understanding")
            for symptom in current_turn_understanding.symptoms:
                trace_notes.append(
                    "understanding:symptom:"
                    f"{symptom.normalized_label_de or symptom.source_label}"
                )
            for match in current_turn_understanding.sts_matches:
                trace_notes.append(f"understanding:sts:{match.sts_id}")

        if raw_safety.requires_safety_clarification and (
            conversation_state.active_question is None
            or conversation_state.active_question.kind != "safety_clarification"
        ):
            conversation_state.active_question = self.safety_clarification_builder.build_active_question(
                safety_state=raw_safety
            )
            conversation_state.phase = "followup"
            return self._ask_existing_question(
                response_input=turn_input,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=current_turn_understanding,
                trace_notes=trace_notes,
                active_question=conversation_state.active_question,
                extra_trace_notes=["turn:safety_clarification_opened"],
            )

        entry_assessment = self.entry_classifier.classify(
            message=turn_input.message,
            active_question=conversation_state.active_question,
            medical_case=medical_case,
            history_messages=turn_input.entry_history_messages,
        )
        trace_notes.append(f"entry:{entry_assessment.message_kind}")

        if not entry_assessment.in_scope:
            decision = TurnDecision(
                kind="out_of_scope",
                response_mode="out_of_scope",
                recommendation_ready=False,
                trace_notes=["turn:out_of_scope"],
            )
            return self._build_result(
                response_input=turn_input,
                decision=decision,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=current_turn_understanding,
                trace_notes=trace_notes,
            )

        extra_case_input = None
        if conversation_state.active_question is not None:
            current_question = conversation_state.active_question
            resolution = self.question_resolver.resolve(
                question=current_question,
                message=turn_input.message,
                history_messages=turn_input.extraction_history_messages,
            )
            trace_notes.extend(resolution.trace_notes)

            if resolution.status.startswith("confirmed_") and current_question.kind == "safety_clarification":
                decision = TurnDecision(
                    kind="ask_safety_question",
                    response_mode="emergency",
                    recommendation_ready=False,
                    trace_notes=["turn:safety_confirmation_emergency"],
                )
                return self._build_result(
                    response_input=turn_input,
                    decision=decision,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    recommendation_state=recommendation_state,
                    symptom_input_draft=symptom_input_draft,
                    current_turn_understanding=current_turn_understanding,
                    trace_notes=trace_notes,
                )

            if resolution.status in {"invalid", "unclear", "still_unclear", "invalid_answer"}:
                decision = TurnDecision(
                    kind="ask_safety_question" if current_question.kind == "safety_clarification" else "ask_followup",
                    response_mode="ask_safety_question" if current_question.kind == "safety_clarification" else "ask_followup",
                    active_question=current_question,
                    recommendation_ready=False,
                    trace_notes=["turn:repeat_active_question"],
                )
                return self._build_result(
                    response_input=turn_input,
                    decision=decision,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    recommendation_state=recommendation_state,
                    symptom_input_draft=symptom_input_draft,
                    current_turn_understanding=current_turn_understanding,
                    trace_notes=trace_notes,
                    active_question=current_question,
                )

            if resolution.clear_active_question:
                if resolution.resolved_followup_id is not None:
                    for need in conversation_state.followup_needs:
                        if need.followup_id == resolution.resolved_followup_id:
                            need.resolved = True
                if resolution.answer_kind == "negated" and current_question.target_observation_id is not None:
                    medical_case = self.case_manager.negate_observation(
                        medical_case=medical_case,
                        observation_id=current_question.target_observation_id,
                    )
                elif resolution.person_update is not None or resolution.observation_patch is not None:
                    if resolution.person_update is not None:
                        medical_case = self.case_manager.update_person(
                            medical_case=medical_case,
                            person_update=resolution.person_update,
                        )
                    elif resolution.observation_patch is not None and current_question.target_observation_id is not None:
                        medical_case = self.case_manager.enrich_observation_from_followup(
                            medical_case=medical_case,
                            observation_id=current_question.target_observation_id,
                            patch=resolution.observation_patch,
                        )
                resolution_additional_information = resolution.additional_medical_information
                extra_case_input = resolution.extra_case_input if resolution.additional_medical_information else None
                resolved_question = current_question
                conversation_state.active_question = None

        case_input = None
        if entry_assessment.message_kind in {"new_case_report", "same_case_update"}:
            case_input = self.medical_extractor.extract(
                message=turn_input.message,
                topic_context=self.case_manager.topic_label(medical_case=medical_case),
                history_messages=turn_input.extraction_history_messages,
            )
        elif extra_case_input is not None and (
            extra_case_input.observations or extra_case_input.topic_entries_to_add
        ):
            case_input = extra_case_input
        elif resolution_additional_information and entry_assessment.contains_new_medical_information:
            case_input = self.medical_extractor.extract(
                message=turn_input.message,
                topic_context=self.case_manager.topic_label(medical_case=medical_case),
                history_messages=turn_input.extraction_history_messages,
            )

        if case_input is not None:
            understanding_has_symptoms = (
                current_turn_understanding is not None
                and bool(current_turn_understanding.symptoms)
            )

            if symptom_input_draft is not None and not understanding_has_symptoms:
                symptom_input_draft = self.symptom_chip_builder.update_from_claims(
                    draft=symptom_input_draft,
                    claims=case_input,
                )
                trace_notes.append("symptom_input_draft:updated_from_claims")
            elif symptom_input_draft is not None and understanding_has_symptoms:
                trace_notes.append("symptom_input_draft:claims_update_skipped_after_understanding")

            medical_case, write_trace = self.case_manager.apply_claims(
                medical_case=medical_case,
                claims=case_input,
            )
            trace_notes.extend(write_trace)
            if case_input.topic_entries_to_add:
                medical_case = self.topic_updater.apply(
                    medical_case=medical_case,
                    topic_entries_to_add=case_input.topic_entries_to_add,
                )
                trace_notes.append("topic:updated")

            if conversation_state.active_question is None or (
                conversation_state.active_question.kind != "safety_clarification"
            ):
                case_safety = self.case_safety_evaluator.evaluate(
                    medical_case=medical_case,
                    current_turn_understanding=current_turn_understanding,
                )
                trace_notes.extend(case_safety.trace_notes)
                if case_safety.requires_safety_clarification:
                    conversation_state.active_question = self.safety_clarification_builder.build_active_question(
                        safety_state=case_safety
                    )
                    conversation_state.phase = "followup"
                    return self._ask_existing_question(
                        response_input=turn_input,
                        medical_case=medical_case,
                        conversation_state=conversation_state,
                        recommendation_state=recommendation_state,
                        symptom_input_draft=symptom_input_draft,
                        current_turn_understanding=current_turn_understanding,
                        trace_notes=trace_notes,
                        active_question=conversation_state.active_question,
                        extra_trace_notes=["turn:case_safety_clarification_selected"],
                    )

        conversation_state.followup_needs = self.followup_need_builder.build(
            medical_case=medical_case,
        )

        followup_need = self.followup_selector.select(followup_needs=conversation_state.followup_needs)
        if followup_need is not None:
            focus_label = None
            if followup_need.observation_id is not None:
                focus_label = self.case_manager.observation_label(
                    medical_case=medical_case,
                    observation_id=followup_need.observation_id,
                )
            conversation_state.active_question = self.question_builder.build_for_need(
                need=followup_need,
                focus_label=focus_label,
            )
            conversation_state.phase = "followup"
            recommendation_state = self.readiness_evaluator.evaluate(
                medical_case=medical_case,
                conversation_state=conversation_state,
            )
            decision = TurnDecision(
                kind="ask_followup",
                response_mode="ask_followup",
                active_question=conversation_state.active_question,
                recommendation_ready=False,
                trace_notes=["turn:followup_selected"],
            )
            return self._build_result(
                response_input=turn_input,
                decision=decision,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=current_turn_understanding,
                trace_notes=trace_notes,
                active_question=conversation_state.active_question,
            )

        recommendation_state = self.readiness_evaluator.evaluate(
            medical_case=medical_case,
            conversation_state=conversation_state,
        )
        assessment_readiness = self.readiness_builder.build(
            medical_case=medical_case,
            conversation_state=conversation_state,
            recommendation_state=recommendation_state,
        )
        trace_notes.extend(assessment_readiness.reason_tags)

        safety_clarification_pending = (
            conversation_state.active_question is not None
            and conversation_state.active_question.kind == "safety_clarification"
        )

        if recommendation_state.recommendation_allowed and not safety_clarification_pending:
            conversation_state.phase = "exploration"
            decision = TurnDecision(
                kind="guide_next_step",
                response_mode="guide_next_step",
                recommendation_ready=True,
                trace_notes=["turn:recommendation_available"],
            )
            return self._build_result(
                response_input=turn_input,
                decision=decision,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=current_turn_understanding,
                trace_notes=trace_notes,
            )

        conversation_state.phase = (
            "exploration"
            if self.case_manager.has_active_observations(medical_case=medical_case)
            else "intake"
        )
        decision = TurnDecision(
            kind="request_case_description",
            response_mode="request_case_description",
            recommendation_ready=False,
            trace_notes=["turn:request_case_description"],
        )
        return self._build_result(
            response_input=turn_input,
            decision=decision,
            medical_case=medical_case,
            conversation_state=conversation_state,
            recommendation_state=recommendation_state,
            symptom_input_draft=symptom_input_draft,
            current_turn_understanding=current_turn_understanding,
            trace_notes=trace_notes,
            resolved_question=resolved_question,
        )

    def request_recommendation(self, request_input: RecommendationRequestInput) -> TurnResult:
        medical_case = request_input.persisted_medical_case or MedicalCase()
        conversation_state = request_input.persisted_conversation_state or ConversationState()
        recommendation_state = request_input.persisted_recommendation_state or RecommendationState()
        symptom_input_draft = request_input.persisted_symptom_input_draft
        trace_notes: list[str] = ["recommendation_request:received"]

        log_event(
            "recommendation.requested",
            layer="application",
            session_id=request_input.session_id,
            turn_id=request_input.turn_id,
            has_topic=self.case_manager.has_topic(medical_case=medical_case),
            has_active_question=conversation_state.active_question is not None,
        )

        recommendation_state = self.readiness_evaluator.evaluate(
            medical_case=medical_case,
            conversation_state=conversation_state,
            request_present=True,
        )

        if conversation_state.active_question is not None:
            return self._ask_existing_question(
                response_input=request_input,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=None,
                trace_notes=trace_notes,
                active_question=conversation_state.active_question,
                extra_trace_notes=["recommendation_request:active_question_blocking"],
            )

        if medical_case is None or not self.case_manager.has_active_observations(medical_case=medical_case):
            decision = TurnDecision(
                kind="request_case_description",
                response_mode="request_case_description",
                recommendation_ready=False,
                trace_notes=["recommendation_request:missing_case_information"],
            )
            return self._build_result(
                response_input=request_input,
                decision=decision,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=None,
                trace_notes=trace_notes,
            )

        conversation_state.followup_needs = self.followup_need_builder.build(
            medical_case=medical_case,
        )
        followup_need = self.followup_selector.select(followup_needs=conversation_state.followup_needs)
        if followup_need is not None:
            focus_label = None
            if followup_need.observation_id is not None:
                focus_label = self.case_manager.observation_label(
                    medical_case=medical_case,
                    observation_id=followup_need.observation_id,
                )
            conversation_state.active_question = self.question_builder.build_for_need(
                need=followup_need,
                focus_label=focus_label,
            )
            conversation_state.phase = "followup"
            recommendation_state = self.readiness_evaluator.evaluate(
                medical_case=medical_case,
                conversation_state=conversation_state,
                request_present=True,
            )
            decision = TurnDecision(
                kind="ask_followup",
                response_mode="ask_followup",
                active_question=conversation_state.active_question,
                recommendation_ready=False,
                trace_notes=["recommendation_request:followup_required"],
            )
            return self._build_result(
                response_input=request_input,
                decision=decision,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=None,
                trace_notes=trace_notes,
                active_question=conversation_state.active_question,
            )

        recommendation_state = self.readiness_evaluator.evaluate(
            medical_case=medical_case,
            conversation_state=conversation_state,
            request_present=True,
        )
        assessment_readiness = self.readiness_builder.build(
            medical_case=medical_case,
            conversation_state=conversation_state,
            recommendation_state=recommendation_state,
        )
        trace_notes.extend(assessment_readiness.reason_tags)

        if recommendation_state.recommendation_allowed:
            recommendation_result = recommendation_state.recommendation_result or self.recommendation_builder.build(
                medical_case=medical_case,
            )
            recommendation_state.recommendation_result = recommendation_result
            recommendation_state.recommendation_allowed = True
            recommendation_state.request_present = True
            conversation_state.active_question = None
            conversation_state.phase = "recommendation"
            decision = TurnDecision(
                kind="recommend",
                response_mode="recommend",
                recommendation_ready=True,
                trace_notes=["recommendation_request:delivered"],
            )
            return self._build_result(
                response_input=request_input,
                decision=decision,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=None,
                trace_notes=trace_notes,
                recommendation_result=recommendation_result,
            )

        decision = TurnDecision(
            kind="request_case_description",
            response_mode="request_case_description",
            recommendation_ready=False,
            trace_notes=["recommendation_request:not_ready"],
        )
        return self._build_result(
            response_input=request_input,
            decision=decision,
            medical_case=medical_case,
            conversation_state=conversation_state,
            recommendation_state=recommendation_state,
            symptom_input_draft=symptom_input_draft,
            current_turn_understanding=None,
            trace_notes=trace_notes,
        )

    def _ask_existing_question(
        self,
        *,
        response_input,
        medical_case: MedicalCase,
        conversation_state: ConversationState,
        recommendation_state: RecommendationState,
        symptom_input_draft,
        current_turn_understanding,
        trace_notes: list[str],
        active_question: ActiveQuestion | None,
        extra_trace_notes: list[str],
    ) -> TurnResult:
        if active_question is not None and active_question.safety_context is not None:
            safety_context = active_question.safety_context
            trace_notes.extend(
                [
                    "safety_clarification:"
                    f"{safety_context.catalog_mapping_status}",
                    *(
                        [f"safety_catalog_reason:{safety_context.consultation_reason_source_id}"]
                        if safety_context.consultation_reason_source_id
                        else []
                    ),
                    *(
                        [f"safety_catalog_criterion:{safety_context.criterion_key}"]
                        if safety_context.criterion_key
                        else []
                    ),
                ]
            )
        decision = TurnDecision(
            kind="ask_safety_question" if active_question is not None and active_question.kind == "safety_clarification" else "ask_followup",
            response_mode="ask_safety_question" if active_question is not None and active_question.kind == "safety_clarification" else "ask_followup",
            active_question=active_question,
            recommendation_ready=False,
            trace_notes=extra_trace_notes,
        )
        return self._build_result(
            response_input=response_input,
            decision=decision,
            medical_case=medical_case,
            conversation_state=conversation_state,
            recommendation_state=recommendation_state,
            symptom_input_draft=symptom_input_draft,
            current_turn_understanding=current_turn_understanding,
            trace_notes=trace_notes,
            active_question=active_question,
        )

    def _build_result(
        self,
        *,
        response_input,
        decision: TurnDecision,
        medical_case: MedicalCase,
        conversation_state: ConversationState,
        recommendation_state: RecommendationState,
        symptom_input_draft,
        current_turn_understanding,
        trace_notes: list[str],
        active_question: ActiveQuestion | None = None,
        recommendation_result=None,
        resolved_question: ActiveQuestion | None = None,
    ) -> TurnResult:
        response_text = self.response_builder.build(
            decision=decision,
            recommendation_result=recommendation_result,
            active_question=active_question,
            medical_case=medical_case,
            conversation_state=conversation_state,
            response_history_messages=getattr(response_input, "response_history_messages", []),
            latest_user_message=getattr(response_input, "message", None),
            resolved_question=resolved_question,
        )
        return TurnResult(
            turn_id=response_input.turn_id,
            response_mode=decision.response_mode,
            response_text=response_text,
            medical_case=medical_case,
            conversation_state=conversation_state,
            recommendation_state=recommendation_state,
            recommendation_result=recommendation_result,
            symptom_input_draft=symptom_input_draft,
            current_turn_understanding=current_turn_understanding,
            trace_notes=trace_notes + decision.trace_notes,
        )
