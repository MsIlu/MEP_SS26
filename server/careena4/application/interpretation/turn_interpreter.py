from __future__ import annotations

import json

from pydantic import ValidationError

from careena4.application.dialogue.safety_clarification_resolver import SafetyClarificationResolver
from careena4.application.interpretation.turn_interpretation_adapters import (
    to_current_turn_understanding as adapt_to_current_turn_understanding,
)
from careena4.application.understanding.sts_consultation_reason_catalog import (
    StsConsultationReasonCatalog,
)
from careena4.core.exceptions import InvalidJSONError, SchemaValidationError
from careena4.core.engine import ExtractionEngine
from careena4.llm.call_control import CallModelConfig, TURN_INTERPRETATION_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import ActiveQuestion, MedicalCase
from careena4.models.turn import EntryAssessment, ExtractedCaseInput, QuestionResolution
from careena4.models.interpretation import TurnInterpretation, TurnUnderstandingSignal
from careena4.models.understanding import StsConsultationReasonCandidate
from careena4.server_log import log_event, log_json


class TurnInterpreter:
    """
    Primary single-call interpreter for one user turn.

    It returns turn signals only. Downstream policy and case writing remain in
    the existing engine and domain layers.
    """

    def __init__(
        self,
        *,
        extraction_engine: ExtractionEngine | None = None,
        call_model_config: CallModelConfig | None = None,
        sts_catalog: StsConsultationReasonCatalog | None = None,
        safety_clarification_resolver: SafetyClarificationResolver | None = None,
    ) -> None:
        self.extraction_engine = extraction_engine
        self.call_model_config = call_model_config
        self.sts_catalog = sts_catalog or StsConsultationReasonCatalog()
        self.safety_clarification_resolver = safety_clarification_resolver or SafetyClarificationResolver()

    def interpret(
        self,
        *,
        message: str,
        active_question: ActiveQuestion | None = None,
        medical_case: MedicalCase | None = None,
        history_messages: list[dict[str, str]] | None = None,
    ) -> TurnInterpretation | None:
        if self.extraction_engine is None:
            return None
        try:
            result = self._extract_interpretation(
                message=message,
                active_question=active_question,
                medical_case=medical_case,
                history_messages=history_messages,
            )
        except Exception as exc:
            log_event(
                "turn_interpretation.fallback_used",
                layer="application",
                reason=type(exc).__name__,
            )
            return None

        result = self._normalize_interpretation(
            message=message,
            active_question=active_question,
            interpretation=result,
        )

        if result.current_turn_understanding is not None:
            hydrated_matches: list[StsConsultationReasonCandidate] = []
            for match in result.current_turn_understanding.sts_matches:
                hydrated = self.sts_catalog.hydrate_match(match.model_dump())
                hydrated_matches.append(StsConsultationReasonCandidate.model_validate(hydrated))
            result.current_turn_understanding.sts_matches = hydrated_matches

        log_event(
            "turn_interpretation.completed",
            layer="application",
            message_kind=result.entry_assessment.message_kind,
            has_question_resolution=result.question_resolution is not None,
            has_case_input=result.case_input is not None,
            symptom_count=(
                len(result.current_turn_understanding.symptoms)
                if result.current_turn_understanding is not None
                else 0
            ),
        )
        return result

    def _extract_interpretation(
        self,
        *,
        message: str,
        active_question: ActiveQuestion | None,
        medical_case: MedicalCase | None,
        history_messages: list[dict[str, str]] | None,
    ) -> TurnInterpretation:
        llm_client = getattr(self.extraction_engine, "llm_client", None)
        if llm_client is None:
            prompt = load_prompt(TURN_INTERPRETATION_CALL)
            return self.extraction_engine.extract(
                text=self._build_user_prompt(
                    message=message,
                    active_question=active_question,
                    medical_case=medical_case,
                    history_messages=history_messages,
                ),
                system_prompt=prompt.system_prompt,
                output_schema=TurnInterpretation,
                temperature=0.0,
                max_tokens=2200,
                model=self.call_model_config.model_for(TURN_INTERPRETATION_CALL) if self.call_model_config is not None else None,
                call_name=TURN_INTERPRETATION_CALL,
                prompt_name=prompt.name,
                prompt_version=prompt.version,
            )
        return self._extract_interpretation_partially(
            llm_client=llm_client,
            message=message,
            active_question=active_question,
            medical_case=medical_case,
            history_messages=history_messages,
        )

    def _extract_interpretation_partially(
        self,
        *,
        llm_client,
        message: str,
        active_question: ActiveQuestion | None,
        medical_case: MedicalCase | None,
        history_messages: list[dict[str, str]] | None,
    ) -> TurnInterpretation:
        prompt = load_prompt(TURN_INTERPRETATION_CALL)
        user_prompt = self._build_user_prompt(
            message=message,
            active_question=active_question,
            medical_case=medical_case,
            history_messages=history_messages,
        )
        selected_model = (
            self.call_model_config.model_for(TURN_INTERPRETATION_CALL)
            if self.call_model_config is not None
            else getattr(llm_client, "default_model", None)
        )

        log_event(
            "llm.extract.started",
            layer="core",
            call_name=TURN_INTERPRETATION_CALL,
            prompt_name=prompt.name,
            prompt_version=prompt.version,
            schema=TurnInterpretation.__name__,
            model=selected_model,
            prompt_chars=len(prompt.system_prompt),
            input_chars=len(user_prompt),
            max_tokens=2200,
            temperature=0.0,
        )
        raw = llm_client.complete(
            messages=[
                {"role": "system", "content": prompt.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=2200,
            model=selected_model,
            json_mode=True,
            call_name=TURN_INTERPRETATION_CALL,
            prompt_name=prompt.name,
            prompt_version=prompt.version,
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            log_event(
                "llm.extract.invalid_json",
                layer="core",
                call_name=TURN_INTERPRETATION_CALL,
                prompt_name=prompt.name,
                prompt_version=prompt.version,
                schema=TurnInterpretation.__name__,
                model=selected_model,
                error=str(exc),
            )
            raise InvalidJSONError(f"Failed to parse LLM JSON response: {exc}") from exc

        entry_payload = parsed.get("entry_assessment")
        try:
            entry_assessment = EntryAssessment.model_validate(entry_payload)
        except ValidationError as exc:
            log_event(
                "llm.extract.schema_validation_failed",
                layer="core",
                call_name=TURN_INTERPRETATION_CALL,
                prompt_name=prompt.name,
                prompt_version=prompt.version,
                schema=TurnInterpretation.__name__,
                model=selected_model,
                error=str(exc),
            )
            raise SchemaValidationError(f"TurnInterpretation entry_assessment validation failed: {exc}") from exc

        question_resolution = self._validate_optional_section(
            section_name="question_resolution",
            payload=parsed.get("question_resolution"),
            model_class=QuestionResolution,
            call_name=TURN_INTERPRETATION_CALL,
            prompt_name=prompt.name,
            prompt_version=prompt.version,
            model=selected_model,
        )
        case_input = self._validate_optional_section(
            section_name="case_input",
            payload=parsed.get("case_input"),
            model_class=ExtractedCaseInput,
            call_name=TURN_INTERPRETATION_CALL,
            prompt_name=prompt.name,
            prompt_version=prompt.version,
            model=selected_model,
        )
        understanding_signal = self._validate_optional_section(
            section_name="current_turn_understanding",
            payload=parsed.get("current_turn_understanding"),
            model_class=TurnUnderstandingSignal,
            call_name=TURN_INTERPRETATION_CALL,
            prompt_name=prompt.name,
            prompt_version=prompt.version,
            model=selected_model,
        )

        trace_notes = [
            note
            for note in parsed.get("trace_notes", [])
            if isinstance(note, str) and note.strip()
        ] if isinstance(parsed.get("trace_notes"), list) else []

        validated = TurnInterpretation(
            entry_assessment=entry_assessment,
            question_resolution=question_resolution,
            case_input=case_input,
            current_turn_understanding=understanding_signal,
            trace_notes=trace_notes,
        )
        log_json(
            f"llm_validated_json:{TURN_INTERPRETATION_CALL}:{TurnInterpretation.__name__}",
            {
                "entry_assessment": validated.entry_assessment.model_dump(),
                "question_resolution": (
                    validated.question_resolution.model_dump()
                    if validated.question_resolution is not None
                    else None
                ),
                "case_input": (
                    validated.case_input.model_dump()
                    if validated.case_input is not None
                    else None
                ),
                "current_turn_understanding": (
                    validated.current_turn_understanding.model_dump()
                    if validated.current_turn_understanding is not None
                    else None
                ),
                "trace_notes": validated.trace_notes,
            },
        )
        log_event(
            "llm.extract.completed",
            layer="core",
            call_name=TURN_INTERPRETATION_CALL,
            prompt_name=prompt.name,
            prompt_version=prompt.version,
            schema=TurnInterpretation.__name__,
            model=selected_model,
        )
        return validated

    @staticmethod
    def _validate_optional_section(
        *,
        section_name: str,
        payload,
        model_class,
        call_name: str,
        prompt_name: str,
        prompt_version: str,
        model: str | None,
    ):
        if payload is None:
            return None
        try:
            return model_class.model_validate(payload)
        except ValidationError as exc:
            log_event(
                "turn_interpretation.partial_section_invalid",
                layer="application",
                section=section_name,
                reason=type(exc).__name__,
                error=str(exc),
            )
            log_event(
                "llm.extract.partial_schema_validation_failed",
                layer="core",
                call_name=call_name,
                prompt_name=prompt_name,
                prompt_version=prompt_version,
                schema=f"TurnInterpretation.{section_name}",
                model=model,
                error=str(exc),
            )
            return None

    def to_current_turn_understanding(
        self,
        *,
        raw_message: str,
        interpretation: TurnInterpretation,
    ):
        return adapt_to_current_turn_understanding(
            raw_message=raw_message,
            interpretation=interpretation,
        )

    def _build_user_prompt(
        self,
        *,
        message: str,
        active_question: ActiveQuestion | None,
        medical_case: MedicalCase | None,
        history_messages: list[dict[str, str]] | None,
    ) -> str:
        history_lines = []
        for item in history_messages or []:
            role = (item.get("role") or "unknown").strip()
            content = (item.get("content") or "").strip()
            if content:
                history_lines.append(f"- {role}: {content}")

        observations = []
        for observation in (medical_case.observations if medical_case is not None else []):
            observations.append(
                {
                    "label": observation.label,
                    "status": observation.status,
                    "person_ref": observation.person_ref,
                    "onset": observation.onset,
                    "body_site": observation.body_site,
                    "severity": observation.severity,
                    "description": observation.description,
                }
            )

        payload = {
            "current_case_topic": {
                "label": medical_case.topic.label if medical_case is not None and medical_case.topic is not None else None,
                "description": medical_case.topic.description if medical_case is not None and medical_case.topic is not None else None,
            },
            "current_case_person": (
                medical_case.person.model_dump()
                if medical_case is not None
                else None
            ),
            "current_case_observations": observations,
            "active_question": (
                {
                    "kind": active_question.kind,
                    "question_intent": active_question.question_intent,
                    "target_observation_id": active_question.target_observation_id,
                    "target_followup_id": active_question.target_followup_id,
                    "prompt_text": active_question.prompt_text,
                    "blocking": active_question.blocking,
                    "allows_additional_medical_info": active_question.allows_additional_medical_info,
                    "guided_input": (
                        {
                            "mode": active_question.guided_input.mode.value,
                            "free_text_allowed": active_question.guided_input.free_text_allowed,
                            "options": [
                                {
                                    "code": option.code,
                                    "label": option.label,
                                    "effect_code": option.effect_code,
                                }
                                for option in active_question.guided_input.options
                            ],
                        }
                        if active_question.guided_input is not None
                        else None
                    ),
                    "safety_context": (
                        {
                            "question_code": active_question.safety_context.question_code,
                            "evidence_terms": list(active_question.safety_context.evidence_terms),
                        }
                        if active_question.safety_context is not None
                        else None
                    ),
                }
                if active_question is not None
                else None
            ),
            "recent_history": history_lines[-4:] if history_lines else [],
            "raw_user_message": message,
            "allowed_sts_consultation_reasons": self.sts_catalog.reasons_for_prompt(),
        }
        return json.dumps(payload, ensure_ascii=False)

    def _normalize_interpretation(
        self,
        *,
        message: str,
        active_question: ActiveQuestion | None,
        interpretation: TurnInterpretation,
    ) -> TurnInterpretation:
        if active_question is None:
            return interpretation

        if interpretation.question_resolution is not None:
            return interpretation

        if not (
            interpretation.entry_assessment.answers_active_question
            or interpretation.entry_assessment.message_kind == "question_answer"
        ):
            return interpretation

        if active_question.kind == "safety_clarification":
            bridged_resolution = self._guided_safety_resolution(
                active_question=active_question,
                message=message,
            )
            if bridged_resolution is not None:
                interpretation.question_resolution = bridged_resolution
                interpretation.trace_notes.append("turn_interpretation:guided_safety_resolution_applied")
                log_event(
                    "turn_interpretation.guided_safety_resolution_applied",
                    layer="application",
                    question_kind=active_question.kind,
                    status=bridged_resolution.status,
                )
                return interpretation

        interpretation.trace_notes.append("turn_interpretation:missing_question_resolution")
        log_event(
            "turn_interpretation.question_resolution_missing",
            layer="application",
            question_kind=active_question.kind,
            question_intent=active_question.question_intent,
            message_kind=interpretation.entry_assessment.message_kind,
        )
        return interpretation

    def _guided_safety_resolution(
        self,
        *,
        active_question: ActiveQuestion,
        message: str,
    ) -> QuestionResolution | None:
        if active_question.kind != "safety_clarification":
            return None

        if active_question.guided_input is None or not active_question.guided_input.options:
            return None

        safety_resolution = self.safety_clarification_resolver.resolve(
            question=active_question,
            answer_code=message.strip(),
        )
        return QuestionResolution(
            status=safety_resolution.outcome.value,
            answer_kind=safety_resolution.outcome.value,
            clear_active_question=safety_resolution.clear_pending_clarification,
            trace_notes=list(safety_resolution.trace_notes),
        )
