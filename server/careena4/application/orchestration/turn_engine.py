from careena4.application.dialogue.question_builder import QuestionBuilder
from careena4.application.dialogue.question_resolver import QuestionResolver
from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.application.dialogue.safety_clarification_builder import SafetyClarificationBuilder
from careena4.application.entry.entry_classifier import EntryClassifier
from careena4.application.extraction.medical_extractor import MedicalExtractor
from careena4.application.input import SymptomChipBuilder
from careena4.application.recommendation.recommendation_builder import RecommendationBuilder
from careena4.application.response.response_builder import ResponseBuilder
from careena4.application.response.response_policy import ResponsePolicy
from careena4.application.topic.case_frame_refiner import CaseFrameRefiner
from careena4.application.topic.topic_manager import TopicManager
from careena4.domain.case import CaseManager
from careena4.domain.quality.followup_need_builder import FollowupNeedBuilder
from careena4.domain.quality.followup_selector import FollowupSelector
from careena4.domain.quality.observation_quality_evaluator import ObservationQualityEvaluator
from careena4.domain.readiness.readiness_evaluator import AssessmentReadinessBuilder, ReadinessEvaluator
from careena4.models.domain import ActiveQuestion, CaseTopic, ConversationState, MedicalCase, RecommendationState
from careena4.application.input import UnderstandingSymptomDraftAdapter
from careena4.application.safety import StructuredRedFlagEvaluator
from careena4.application.understanding import MedGemmaTurnUnderstandingService
from careena4.models.safety import CurrentTurnSafetyEvidence
from careena4.models.turn import TurnDecision, TurnInput, TurnResult
from careena4.server_log import log_event


class TurnEngine:
    def __init__(
        self,
        *,
        raw_red_flag_detector: RawRedFlagDetector | None = None,
        safety_clarification_builder: SafetyClarificationBuilder | None = None,
        entry_classifier: EntryClassifier | None = None,
        question_resolver: QuestionResolver | None = None,
        topic_manager: TopicManager | None = None,
        case_frame_refiner: CaseFrameRefiner | None = None,
        medical_extractor: MedicalExtractor | None = None,
        case_manager: CaseManager | None = None,
        quality_evaluator: ObservationQualityEvaluator | None = None,
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
        structured_red_flag_evaluator: StructuredRedFlagEvaluator | None = None,
    ):
        self.raw_red_flag_detector = raw_red_flag_detector or RawRedFlagDetector()
        self.safety_clarification_builder = safety_clarification_builder or SafetyClarificationBuilder()
        self.case_manager = case_manager or CaseManager()
        self.entry_classifier = entry_classifier or EntryClassifier(case_manager=self.case_manager)
        self.question_resolver = question_resolver or QuestionResolver()
        self.topic_manager = topic_manager or TopicManager(case_manager=self.case_manager)
        self.case_frame_refiner = case_frame_refiner or CaseFrameRefiner(case_manager=self.case_manager)
        self.medical_extractor = medical_extractor or MedicalExtractor()
        self.symptom_chip_builder = SymptomChipBuilder()
        self.quality_evaluator = quality_evaluator or ObservationQualityEvaluator(case_manager=self.case_manager)
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
        self.structured_red_flag_evaluator = structured_red_flag_evaluator or StructuredRedFlagEvaluator()

    def run_turn(self, turn_input: TurnInput) -> TurnResult:
        case_topic = turn_input.persisted_case_topic
        medical_case = turn_input.persisted_medical_case or MedicalCase()
        medical_case = self.case_manager.sync_legacy_topic_projection(
            medical_case=medical_case,
            case_topic=case_topic,
        )
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
            has_case_topic=case_topic is not None,
            has_medical_case=turn_input.persisted_medical_case is not None,
            has_active_question=conversation_state.active_question is not None,
        )

        raw_safety = self.raw_red_flag_detector.detect(turn_input.message)
        trace_notes.extend(raw_safety.trace_notes)
        if raw_safety.requires_emergency_response:
            decision = TurnDecision(
                kind="ask_safety_question",
                response_mode="emergency",
                recommendation_requested=conversation_state.recommendation_requested,
                recommendation_ready=False,
                trace_notes=["turn:emergency_shortcut"],
            )
            response_text = self._build_response_text(
                turn_input=turn_input,
                decision=decision,
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
            )
            return TurnResult(
                turn_id=turn_input.turn_id,
                response_mode=decision.response_mode,
                response_text=response_text,
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=current_turn_understanding,
                trace_notes=trace_notes + decision.trace_notes,
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

        if current_turn_understanding is not None and current_turn_understanding.symptoms:
            structured_safety_evidence = CurrentTurnSafetyEvidence.from_turn_understanding(
                raw_message=turn_input.message,
                understanding=current_turn_understanding,
            )
            structured_safety = self.structured_red_flag_evaluator.evaluate(
                evidence=structured_safety_evidence,
            )
            trace_notes.extend(structured_safety.trace_notes)

            if structured_safety.requires_emergency_response:
                decision = TurnDecision(
                    kind="ask_safety_question",
                    response_mode="emergency",
                    recommendation_requested=conversation_state.recommendation_requested,
                    recommendation_ready=False,
                    trace_notes=["turn:structured_emergency_shortcut"],
                )
                response_text = self._build_response_text(
                    turn_input=turn_input,
                    decision=decision,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                )
                return TurnResult(
                    turn_id=turn_input.turn_id,
                    response_mode=decision.response_mode,
                    response_text=response_text,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    recommendation_state=recommendation_state,
                    symptom_input_draft=symptom_input_draft,
                    current_turn_understanding=current_turn_understanding,
                    trace_notes=trace_notes + decision.trace_notes,
                )

            if structured_safety.requires_safety_clarification and (
                conversation_state.active_question is None
                or conversation_state.active_question.kind != "safety_clarification"
            ):
                conversation_state.active_question = self.safety_clarification_builder.build_active_question(
                    safety_state=structured_safety.to_safety_state()
                )
                conversation_state.phase = "followup"

                active_question = conversation_state.active_question
                safety_context = active_question.safety_context if active_question is not None else None
                trace_notes.extend(
                    [
                        "safety_clarification:"
                        f"{safety_context.catalog_mapping_status if safety_context is not None else 'unknown'}",
                        "turn:structured_safety_clarification_opened",
                    ]
                )

                decision = TurnDecision(
                    kind="ask_safety_question",
                    response_mode="ask_safety_question",
                    active_question=active_question,
                    recommendation_requested=conversation_state.recommendation_requested,
                    recommendation_ready=False,
                    trace_notes=["turn:safety_clarification_selected"],
                )
                response_text = self._build_response_text(
                    turn_input=turn_input,
                    decision=decision,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    active_question=active_question,
                )
                return TurnResult(
                    turn_id=turn_input.turn_id,
                    response_mode=decision.response_mode,
                    response_text=response_text,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    recommendation_state=recommendation_state,
                    symptom_input_draft=symptom_input_draft,
                    current_turn_understanding=current_turn_understanding,
                    trace_notes=trace_notes + decision.trace_notes,
                )

        if raw_safety.requires_safety_clarification and (
            conversation_state.active_question is None
            or conversation_state.active_question.kind != "safety_clarification"
        ):
            conversation_state.active_question = self.safety_clarification_builder.build_active_question(
                safety_state=raw_safety
            )
            conversation_state.phase = "followup"

            active_question = conversation_state.active_question
            safety_context = active_question.safety_context if active_question is not None else None
            trace_notes.extend(
                [
                    "safety_clarification:"
                    f"{safety_context.catalog_mapping_status if safety_context is not None else 'unknown'}",
                    *(
                        [
                            "safety_catalog_reason:"
                            f"{safety_context.consultation_reason_source_id}"
                        ]
                        if safety_context is not None
                        and safety_context.consultation_reason_source_id
                        else []
                    ),
                    *(
                        [
                            "safety_catalog_criterion:"
                            f"{safety_context.criterion_key}"
                        ]
                        if safety_context is not None
                        and safety_context.criterion_key
                        else []
                    ),
                ]
            )

            decision = TurnDecision(
                kind="ask_safety_question",
                response_mode="ask_safety_question",
                active_question=active_question,
                recommendation_requested=conversation_state.recommendation_requested,
                recommendation_ready=False,
                trace_notes=["turn:safety_clarification_opened"],
            )
            response_text = self._build_response_text(
                turn_input=turn_input,
                decision=decision,
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
                active_question=active_question,
            )
            return TurnResult(
                turn_id=turn_input.turn_id,
                response_mode=decision.response_mode,
                response_text=response_text,
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=current_turn_understanding,
                trace_notes=trace_notes + decision.trace_notes,
            )

        entry_assessment = self.entry_classifier.classify(
            message=turn_input.message,
            active_question=conversation_state.active_question,
            case_topic=case_topic,
            history_messages=turn_input.entry_history_messages,
        )
        trace_notes.append(f"entry:{entry_assessment.message_kind}")
        if entry_assessment.recommendation_requested:
            conversation_state.recommendation_requested = True
        recommendation_state.request_present = conversation_state.recommendation_requested

        if not entry_assessment.in_scope:
            decision = TurnDecision(
                kind="out_of_scope",
                response_mode="out_of_scope",
                recommendation_requested=conversation_state.recommendation_requested,
                recommendation_ready=False,
                trace_notes=["turn:out_of_scope"],
            )
            response_text = self._build_response_text(
                turn_input=turn_input,
                decision=decision,
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
            )
            return TurnResult(
                turn_id=turn_input.turn_id,
                response_mode=decision.response_mode,
                response_text=response_text,
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=current_turn_understanding,
                trace_notes=trace_notes + decision.trace_notes,
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
                    recommendation_requested=conversation_state.recommendation_requested,
                    recommendation_ready=False,
                    trace_notes=["turn:safety_confirmation_emergency"],
                )
                response_text = self._build_response_text(
                    turn_input=turn_input,
                    decision=decision,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                )
                return TurnResult(
                    turn_id=turn_input.turn_id,
                    response_mode=decision.response_mode,
                    response_text=response_text,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    recommendation_state=recommendation_state,
                    symptom_input_draft=symptom_input_draft,
                    current_turn_understanding=current_turn_understanding,
                    trace_notes=trace_notes + decision.trace_notes,
                )

            if resolution.status in {"invalid", "unclear", "still_unclear", "invalid_answer"}:
                decision = TurnDecision(
                    kind="ask_safety_question" if current_question.kind == "safety_clarification" else "ask_followup",
                    response_mode="ask_safety_question" if current_question.kind == "safety_clarification" else "ask_followup",
                    active_question=current_question,
                    recommendation_requested=conversation_state.recommendation_requested,
                    recommendation_ready=False,
                    trace_notes=["turn:repeat_active_question"],
                )
                response_text = self._build_response_text(
                    turn_input=turn_input,
                    decision=decision,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    active_question=current_question,
                )
                return TurnResult(
                    turn_id=turn_input.turn_id,
                    response_mode=decision.response_mode,
                    response_text=response_text,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    recommendation_state=recommendation_state,
                    symptom_input_draft=symptom_input_draft,
                    current_turn_understanding=current_turn_understanding,
                    trace_notes=trace_notes + decision.trace_notes,
                )

            if resolution.recommendation_choice == "recommendation_now":
                recommendation_state = self.readiness_evaluator.evaluate(
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                )
                recommendation_result = self.recommendation_builder.build(
                    case_topic=case_topic,
                    medical_case=medical_case,
                )
                recommendation_state.recommendation_result = recommendation_result
                recommendation_state.recommendation_allowed = True
                conversation_state.active_question = None
                conversation_state.phase = "recommendation"
                decision = TurnDecision(
                    kind="recommend",
                    response_mode="recommend",
                    recommendation_requested=conversation_state.recommendation_requested,
                    recommendation_ready=True,
                    trace_notes=["turn:recommendation_committed"],
                )
                response_text = self._build_response_text(
                    turn_input=turn_input,
                    decision=decision,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    recommendation_result=recommendation_result,
                )
                return TurnResult(
                    turn_id=turn_input.turn_id,
                    response_mode=decision.response_mode,
                    response_text=response_text,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    recommendation_state=recommendation_state,
                    symptom_input_draft=symptom_input_draft,
                    current_turn_understanding=current_turn_understanding,
                    recommendation_result=recommendation_result,
                    trace_notes=trace_notes + decision.trace_notes,
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
                        medical_case, case_topic = self.case_manager.update_person(
                            medical_case=medical_case,
                            person_update=resolution.person_update,
                            case_topic=case_topic,
                        )
                    elif resolution.observation_patch is not None and current_question.target_observation_id is not None:
                        medical_case = self.case_manager.enrich_observation_from_followup(
                            medical_case=medical_case,
                            observation_id=current_question.target_observation_id,
                            patch=resolution.observation_patch,
                        )
                case_topic = self.case_frame_refiner.refine(case_topic=case_topic, medical_case=medical_case)
                medical_case = self.case_manager.sync_legacy_topic_projection(
                    medical_case=medical_case,
                    case_topic=case_topic,
                )
                resolution_additional_information = resolution.additional_medical_information
                extra_case_input = resolution.extra_case_input if resolution.additional_medical_information else None
                resolved_question = current_question
                conversation_state.active_question = None
                if current_question.kind == "closing_choice" and resolution.recommendation_choice == "add_more_information":
                    conversation_state.phase = "exploration"
                    if not resolution.additional_medical_information:
                        conversation_state.active_question = self.question_builder.build_additional_information_request()
                        decision = TurnDecision(
                            kind="ask_followup",
                            response_mode="ask_followup",
                            active_question=conversation_state.active_question,
                            recommendation_requested=conversation_state.recommendation_requested,
                            recommendation_ready=recommendation_state.recommendation_allowed,
                            trace_notes=["turn:additional_information_requested"],
                        )
                        response_text = self._build_response_text(
                            turn_input=turn_input,
                            decision=decision,
                            case_topic=case_topic,
                            medical_case=medical_case,
                            conversation_state=conversation_state,
                            active_question=conversation_state.active_question,
                        )
                        return TurnResult(
                            turn_id=turn_input.turn_id,
                            response_mode=decision.response_mode,
                            response_text=response_text,
                            case_topic=case_topic,
                            medical_case=medical_case,
                            conversation_state=conversation_state,
                            recommendation_state=recommendation_state,
                            symptom_input_draft=symptom_input_draft,
                            current_turn_understanding=current_turn_understanding,
                            trace_notes=trace_notes + decision.trace_notes,
                        )

        case_input = None
        if entry_assessment.message_kind in {"new_case_report", "same_case_update"}:
            case_input = self.medical_extractor.extract(
                message=turn_input.message,
                case_topic=self.case_manager.topic_label(case_topic=case_topic),
                history_messages=turn_input.extraction_history_messages,
            )
        elif extra_case_input is not None and extra_case_input.observations:
            case_input = extra_case_input
        elif resolution_additional_information and entry_assessment.contains_new_medical_information:
            case_input = self.medical_extractor.extract(
                message=turn_input.message,
                case_topic=self.case_manager.topic_label(case_topic=case_topic),
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

            case_topic = self.topic_manager.ensure_topic(
                existing_topic=case_topic,
                medical_case=medical_case,
                claims=case_input,
                latest_message=turn_input.message,
                turn_id=turn_input.turn_id,
            )
            medical_case = self.case_manager.sync_legacy_topic_projection(
                medical_case=medical_case,
                case_topic=case_topic,
            )
            conversation_state.topic_fit_state = self.topic_manager.evaluate_topic_fit(
                case_topic=case_topic,
                message=turn_input.message,
                claims=case_input,
            )
            topic_mismatch = (
                case_topic is not None
                and conversation_state.topic_fit_state == "mismatch"
                and entry_assessment.message_kind == "same_case_update"
            )
            if topic_mismatch:
                conversation_state.off_topic_state = "active"
                decision = TurnDecision(
                    kind="out_of_scope",
                    response_mode="out_of_scope",
                    recommendation_requested=conversation_state.recommendation_requested,
                    recommendation_ready=False,
                    trace_notes=["turn:topic_mismatch"],
                )
                response_text = self._build_response_text(
                    turn_input=turn_input,
                    decision=decision,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    topic_mismatch=True,
                )
                return TurnResult(
                    turn_id=turn_input.turn_id,
                    response_mode=decision.response_mode,
                    response_text=response_text,
                    case_topic=case_topic,
                    medical_case=medical_case,
                    conversation_state=conversation_state,
                    recommendation_state=recommendation_state,
                    symptom_input_draft=symptom_input_draft,
                    current_turn_understanding=current_turn_understanding,
                    trace_notes=trace_notes + decision.trace_notes,
                )
            medical_case, write_trace = self.case_manager.apply_claims(
                medical_case=medical_case,
                claims=case_input,
                case_topic=case_topic,
            )
            trace_notes.extend(write_trace)
            case_topic = self.case_frame_refiner.refine(case_topic=case_topic, medical_case=medical_case)
            medical_case = self.case_manager.sync_legacy_topic_projection(
                medical_case=medical_case,
                case_topic=case_topic,
            )
        elif case_topic is not None:
            case_topic = self.case_frame_refiner.refine(case_topic=case_topic, medical_case=medical_case)
            medical_case = self.case_manager.sync_legacy_topic_projection(
                medical_case=medical_case,
                case_topic=case_topic,
            )

        qualities = self.quality_evaluator.evaluate(case_topic=case_topic, medical_case=medical_case)
        conversation_state.followup_needs = self.followup_need_builder.build(
            case_topic=case_topic,
            medical_case=medical_case,
            qualities=qualities,
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
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
            )
            decision = TurnDecision(
                kind="ask_followup",
                response_mode="ask_followup",
                active_question=conversation_state.active_question,
                recommendation_requested=conversation_state.recommendation_requested,
                recommendation_ready=False,
                trace_notes=["turn:followup_selected"],
            )
            response_text = self._build_response_text(
                turn_input=turn_input,
                decision=decision,
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
                active_question=conversation_state.active_question,
            )
            return TurnResult(
                turn_id=turn_input.turn_id,
                response_mode=decision.response_mode,
                response_text=response_text,
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=current_turn_understanding,
                trace_notes=trace_notes + decision.trace_notes,
            )

        recommendation_state = self.readiness_evaluator.evaluate(
            case_topic=case_topic,
            medical_case=medical_case,
            conversation_state=conversation_state,
        )
        assessment_readiness = self.readiness_builder.build(
            case_topic=case_topic,
            medical_case=medical_case,
            conversation_state=conversation_state,
            recommendation_state=recommendation_state,
        )
        trace_notes.extend(assessment_readiness.reason_tags)

        if recommendation_state.recommendation_allowed:
            conversation_state.active_question = self.question_builder.build_closing_choice()
            conversation_state.phase = "closing_check"
            recommendation_state.closing_prompt_active = True
            decision = TurnDecision(
                kind="guide_next_step",
                response_mode="guide_next_step",
                active_question=conversation_state.active_question,
                recommendation_requested=conversation_state.recommendation_requested,
                recommendation_ready=True,
                trace_notes=["turn:closing_choice_opened"],
            )
            response_text = self._build_response_text(
                turn_input=turn_input,
                decision=decision,
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
                active_question=conversation_state.active_question,
            )
            return TurnResult(
                turn_id=turn_input.turn_id,
                response_mode=decision.response_mode,
                response_text=response_text,
                case_topic=case_topic,
                medical_case=medical_case,
                conversation_state=conversation_state,
                recommendation_state=recommendation_state,
                symptom_input_draft=symptom_input_draft,
                current_turn_understanding=current_turn_understanding,
                trace_notes=trace_notes + decision.trace_notes,
            )

        # If we have no explicit next question and are not ready, we fall back to an explicit
        # case-description request instead of exposing an open-ended "continue" state.
        conversation_state.phase = (
            "exploration"
            if self.case_manager.has_active_observations(medical_case=medical_case)
            else "intake"
        )
        decision = TurnDecision(
            kind="request_case_description",
            response_mode="request_case_description",
            recommendation_requested=conversation_state.recommendation_requested,
            recommendation_ready=False,
            trace_notes=["turn:request_case_description"],
        )
        response_text = self._build_response_text(
            turn_input=turn_input,
            decision=decision,
            case_topic=case_topic,
            medical_case=medical_case,
            conversation_state=conversation_state,
        )
        return TurnResult(
            turn_id=turn_input.turn_id,
            response_mode=decision.response_mode,
            response_text=response_text,
            case_topic=case_topic,
            medical_case=medical_case,
            conversation_state=conversation_state,
            recommendation_state=recommendation_state,
            symptom_input_draft=symptom_input_draft,
            current_turn_understanding=current_turn_understanding,
            trace_notes=trace_notes + decision.trace_notes,
        )

    def _build_response_text(
        self,
        *,
        turn_input: TurnInput,
        decision: TurnDecision,
        case_topic: CaseTopic | None,
        medical_case: MedicalCase,
        conversation_state: ConversationState,
        active_question: ActiveQuestion | None = None,
        recommendation_result=None,
        topic_mismatch: bool = False,
        resolved_question: ActiveQuestion | None = None,
    ) -> str:
        return self.response_builder.build(
            decision=decision,
            recommendation_result=recommendation_result,
            active_question=active_question,
            topic_mismatch=topic_mismatch,
            case_topic=case_topic,
            medical_case=medical_case,
            conversation_state=conversation_state,
            response_history_messages=turn_input.response_history_messages,
            latest_user_message=turn_input.message,
            resolved_question=resolved_question,
        )

