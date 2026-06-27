from __future__ import annotations

import re

from careena4.application.dialogue.safety_clarification_resolver import SafetyClarificationResolver
from careena4.application.extraction.medical_extractor import MedicalExtractor
from careena4.core.engine import ExtractionEngine
from careena4.llm.call_control import CallModelConfig, FOLLOWUP_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import ActiveQuestion, Source
from careena4.models.turn import ExtractedCaseInput, ObservationPatch, PersonUpdate, QuestionResolution
from careena4.server_log import log_event


class QuestionResolver:
    def __init__(
        self,
        *,
        safety_clarification_resolver: SafetyClarificationResolver | None = None,
        medical_extractor: MedicalExtractor | None = None,
        extraction_engine: ExtractionEngine | None = None,
        call_model_config: CallModelConfig | None = None,
    ):
        self.safety_clarification_resolver = safety_clarification_resolver or SafetyClarificationResolver()
        self.medical_extractor = medical_extractor or MedicalExtractor()
        self.extraction_engine = extraction_engine
        self.call_model_config = call_model_config

    def resolve(
        self,
        *,
        question: ActiveQuestion,
        message: str,
        history_messages: list[dict[str, str]] | None = None,
    ) -> QuestionResolution:
        stripped = message.strip()
        normalized = self._normalize(stripped)

        if question.kind == "safety_clarification":
            safety_resolution = self.safety_clarification_resolver.resolve(question=question, answer_code=stripped)
            return QuestionResolution(
                status=safety_resolution.outcome.value,
                answer_kind=safety_resolution.outcome.value,
                clear_active_question=safety_resolution.clear_pending_clarification,
                trace_notes=list(safety_resolution.trace_notes),
            )
        if question.kind == "subject_clarification":
            return self._resolve_without_llm(
                question=question,
                message=message,
                normalized=normalized,
                stripped=stripped,
            )

        if question.kind == "closing_choice":
            additional_medical_information = self._contains_additional_medical_info(normalized)
            extra_case_input = (
                self._extra_case_input_if_needed(question=question, message=message)
                if additional_medical_information
                else None
            )
            if self._is_add_more_information_choice(normalized):
                return QuestionResolution(
                    status="resolved",
                    answer_kind="add_more_information",
                    clear_active_question=True,
                    recommendation_choice="add_more_information",
                    additional_medical_information=additional_medical_information,
                    extra_case_input=extra_case_input,
                    trace_notes=["closing_choice:add_more_information"],
                )
            if additional_medical_information:
                return QuestionResolution(
                    status="resolved",
                    answer_kind="add_more_information",
                    clear_active_question=True,
                    recommendation_choice="add_more_information",
                    additional_medical_information=True,
                    extra_case_input=extra_case_input,
                    trace_notes=["closing_choice:add_more_information_from_medical_input"],
                )
            if self._is_recommendation_now_choice(normalized):
                return QuestionResolution(
                    status="resolved",
                    answer_kind="recommendation_now",
                    clear_active_question=True,
                    recommendation_choice="recommendation_now",
                    trace_notes=["closing_choice:recommendation_now"],
                )
            return QuestionResolution(
                status="unclear",
                answer_kind="unclear",
                clear_active_question=False,
                trace_notes=["closing_choice:unclear"],
            )

        llm_result = self._resolve_with_llm(
            question=question,
            message=message,
            history_messages=history_messages,
        )
        if llm_result is not None:
            return llm_result
        return self._resolve_without_llm(
            question=question,
            message=message,
            normalized=normalized,
            stripped=stripped,
        )

    def _resolve_with_llm(
        self,
        *,
        question: ActiveQuestion,
        message: str,
        history_messages: list[dict[str, str]] | None,
    ) -> QuestionResolution | None:
        if self.extraction_engine is None:
            return None
        prompt = load_prompt(FOLLOWUP_CALL)
        try:
            result = self.extraction_engine.extract(
                text=self._build_user_prompt(
                    question=question,
                    message=message,
                    history_messages=history_messages,
                ),
                system_prompt=prompt.system_prompt,
                output_schema=QuestionResolution,
                temperature=0.0,
                max_tokens=900,
                model=self.call_model_config.model_for(FOLLOWUP_CALL) if self.call_model_config is not None else None,
                call_name=FOLLOWUP_CALL,
                prompt_name=prompt.name,
                prompt_version=prompt.version,
            )
        except Exception as exc:
            log_event(
                "followup.resolution.fallback_used",
                layer="application",
                question_kind=question.kind,
                question_intent=question.question_intent,
                reason=type(exc).__name__,
            )
            return QuestionResolution(
                status="unclear",
                answer_kind="unclear",
                clear_active_question=False,
                trace_notes=["followup:llm_resolution_failed"],
            )

        result = self._canonicalize_resolution(question=question, resolution=result)
        result = self._validate_resolution(question=question, resolution=result)

        log_event(
            "followup.resolution.completed",
            layer="application",
            question_kind=question.kind,
            question_intent=question.question_intent,
            status=result.status,
            answer_kind=result.answer_kind,
            additional_medical_information=result.additional_medical_information,
            update_keys=",".join(self._resolution_field_keys(result)) or "none",
        )
        return result

    def _resolve_without_llm(
        self,
        *,
        question: ActiveQuestion,
        message: str,
        normalized: str,
        stripped: str,
    ) -> QuestionResolution:
        if question.kind == "subject_clarification":
            def _observation_person_patch(relation: str, source: Source | None) -> ObservationPatch:
                return ObservationPatch(person_ref=relation, person_ref_source=source)

            if "kind" in normalized or "sohn" in normalized or "tochter" in normalized:
                source = self._first_source(normalized, ("kind", "sohn", "tochter"))
                return QuestionResolution(
                    status="resolved",
                    answer_kind="subject_child",
                    clear_active_question=True,
                    resolved_followup_id=question.target_followup_id,
                    person_update=None if question.target_observation_id is not None else PersonUpdate(
                        relation="child",
                        relation_source=source,
                    ),
                    observation_patch=(
                        _observation_person_patch("child", source)
                        if question.target_observation_id is not None
                        else None
                    ),
                    additional_medical_information=self._contains_additional_medical_info(normalized),
                    extra_case_input=self._extra_case_input_if_needed(question=question, message=message),
                )
            if "andere" in normalized or "mutter" in normalized or "vater" in normalized:
                source = self._first_source(normalized, ("andere", "mutter", "vater"))
                return QuestionResolution(
                    status="resolved",
                    answer_kind="subject_other",
                    clear_active_question=True,
                    resolved_followup_id=question.target_followup_id,
                    person_update=None if question.target_observation_id is not None else PersonUpdate(
                        relation="other",
                        relation_source=source,
                    ),
                    observation_patch=(
                        _observation_person_patch("other", source)
                        if question.target_observation_id is not None
                        else None
                    ),
                    additional_medical_information=self._contains_additional_medical_info(normalized),
                    extra_case_input=self._extra_case_input_if_needed(question=question, message=message),
                )
            if "ich" in normalized or "selbst" in normalized:
                source = self._first_source(normalized, ("ich", "selbst"))
                return QuestionResolution(
                    status="resolved",
                    answer_kind="subject_self",
                    clear_active_question=True,
                    resolved_followup_id=question.target_followup_id,
                    person_update=None if question.target_observation_id is not None else PersonUpdate(
                        relation="self",
                        relation_source=source,
                    ),
                    observation_patch=(
                        _observation_person_patch("self", source)
                        if question.target_observation_id is not None
                        else None
                    ),
                    additional_medical_information=self._contains_additional_medical_info(normalized),
                    extra_case_input=self._extra_case_input_if_needed(question=question, message=message),
                )
            return QuestionResolution(
                status="unclear",
                answer_kind="unclear",
                trace_notes=["subject_clarification:unclear"],
            )

        if not stripped:
            return QuestionResolution(
                status="invalid",
                answer_kind="invalid",
                trace_notes=["followup:invalid_empty"],
            )
        if self._looks_unclear(normalized):
            return QuestionResolution(
                status="unclear",
                answer_kind="unclear",
                trace_notes=["followup:unclear_answer"],
            )
        if self._looks_negated(normalized):
            return QuestionResolution(
                status="resolved",
                answer_kind="negated",
                clear_active_question=True,
                resolved_followup_id=question.target_followup_id,
                trace_notes=["followup:resolved:negated"],
            )

        observation_patch = self._patch_for_intent(
            question_intent=question.question_intent,
            value=stripped,
        )
        answer_kind = {
            "duration": "duration_provided",
            "description": "description_provided",
            "severity": "severity_provided",
        }.get(question.question_intent, "resolved")
        result = QuestionResolution(
            status="resolved",
            answer_kind=answer_kind,
            clear_active_question=True,
            resolved_followup_id=question.target_followup_id,
            observation_patch=observation_patch,
            additional_medical_information=False,
            extra_case_input=None,
            trace_notes=[f"followup:resolved:{question.question_intent or 'generic'}"],
        )
        result = self._canonicalize_resolution(question=question, resolution=result)
        return self._validate_resolution(question=question, resolution=result)

    def _canonicalize_resolution(
        self,
        *,
        question: ActiveQuestion,
        resolution: QuestionResolution,
    ) -> QuestionResolution:
        if resolution.status == "resolved":
            resolution.clear_active_question = True
            if question.target_followup_id is not None and resolution.resolved_followup_id is None:
                resolution.resolved_followup_id = question.target_followup_id
        if not resolution.additional_medical_information:
            resolution.extra_case_input = None
        return resolution

    def _validate_resolution(
        self,
        *,
        question: ActiveQuestion,
        resolution: QuestionResolution,
    ) -> QuestionResolution:
        if question.kind != "followup":
            return resolution

        if resolution.answer_kind in {None, ""}:
            return QuestionResolution(
                status="invalid",
                answer_kind="invalid",
                clear_active_question=False,
                trace_notes=["followup:invalid_missing_answer_kind"],
            )

        if resolution.answer_kind == "negated":
            resolution.status = "resolved"
            resolution.clear_active_question = True
            resolution.observation_patch = None
            return resolution

        if resolution.answer_kind in {"unclear", "invalid"}:
            resolution.status = resolution.answer_kind
            resolution.clear_active_question = False
            resolution.person_update = None
            resolution.observation_patch = None
            resolution.extra_case_input = None
            return resolution

        expected_field = {
            "duration": "onset",
            "description": "description",
            "severity": "severity",
        }.get(question.question_intent)
        allowed_answer_kinds = {
            "duration": {"duration_provided", "duration_plus_more", "negated", "unclear", "invalid"},
            "description": {"description_provided", "description_plus_more", "negated", "unclear", "invalid"},
            "severity": {"severity_provided", "severity_plus_more", "negated", "unclear", "invalid"},
        }.get(question.question_intent)

        if expected_field is None or allowed_answer_kinds is None:
            return resolution
        if resolution.answer_kind not in allowed_answer_kinds:
            return QuestionResolution(
                status="invalid",
                answer_kind="invalid",
                clear_active_question=False,
                trace_notes=[f"followup:invalid_answer_kind:{resolution.answer_kind}"],
            )
        if resolution.answer_kind.endswith("_provided") or resolution.answer_kind.endswith("_plus_more"):
            if resolution.observation_patch is None:
                return QuestionResolution(
                    status="invalid",
                    answer_kind="invalid",
                    clear_active_question=False,
                    trace_notes=[f"followup:missing_expected_attribute:{expected_field}"],
                )
            value = getattr(resolution.observation_patch, expected_field)
            if value in (None, "", []):
                return QuestionResolution(
                    status="invalid",
                    answer_kind="invalid",
                    clear_active_question=False,
                    trace_notes=[f"followup:missing_expected_attribute:{expected_field}"],
                )
            if resolution.answer_kind.endswith("_plus_more") and (
                not resolution.additional_medical_information or resolution.extra_case_input is None
            ):
                return QuestionResolution(
                    status="invalid",
                    answer_kind="invalid",
                    clear_active_question=False,
                    trace_notes=["followup:missing_extra_case_input_for_plus_more"],
                )
            resolution.status = "resolved"
            resolution.clear_active_question = True
            if resolution.answer_kind.endswith("_provided"):
                resolution.additional_medical_information = False
                resolution.extra_case_input = None
            return resolution
        return resolution

    def _build_user_prompt(
        self,
        *,
        question: ActiveQuestion,
        message: str,
        history_messages: list[dict[str, str]] | None,
    ) -> str:
        history_lines = []
        for item in history_messages or []:
            role = (item.get("role") or "unknown").strip()
            content = (item.get("content") or "").strip()
            if content:
                history_lines.append(f"- {role}: {content}")
        history_text = "\n".join(history_lines[-4:]) if history_lines else "- none"
        return (
            f"ActiveQuestion kind={question.kind}\n"
            f"question_intent={question.question_intent}\n"
            f"target_observation_id={question.target_observation_id or 'none'}\n"
            f"target_followup_id={question.target_followup_id or 'none'}\n"
            f"prompt_text={question.prompt_text}\n"
            f"blocking={question.blocking}\n"
            f"Letzte Konversation:\n{history_text}\n"
            f"Letzte Nutzernachricht:\n{message}"
        )

    def _extra_case_input_if_needed(self, *, question: ActiveQuestion, message: str) -> ExtractedCaseInput | None:
        if not question.allows_additional_medical_info:
            return None
        case_input = self.medical_extractor.extract(message=message)
        if (
            case_input.person is None
            and not case_input.observations
            and not case_input.topic_entries_to_add
        ):
            return None
        return case_input

    @staticmethod
    def _contains_additional_medical_info(normalized: str) -> bool:
        return bool(
            re.search(
                r"\b(schmerz|weh|zieht|stech|dumpf|druck|fieber|husten|atem|sturz|fahrradsturz|verletzt|arzt|uebel|erbrechen|durchfall|hueft|kopf|bauch|brust|hals|bein|arm|leiste)\b",
                normalized,
            )
        )

    @staticmethod
    def _is_add_more_information_choice(normalized: str) -> bool:
        return any(
            phrase in normalized
            for phrase in (
                "nein, weitere angaben",
                "nein weitere angaben",
                "weitere angaben",
                "mehr angaben",
                "mehr informationen",
                "mehr info",
                "weiter",
                "hinzufuegen",
                "hinzufÃƒÂ¼gen",
                "noch",
                "angaben",
            )
        )

    @staticmethod
    def _is_recommendation_now_choice(normalized: str) -> bool:
        return any(
            phrase in normalized
            for phrase in (
                "ja, empfehlung",
                "ja empfehlung",
                "empfehlung",
                "versorgungsempfehlung",
                "ja",
                "okay",
                "ok",
                "passt",
                "reicht",
                "wars",
                "wÃƒÂ¤rs",
                "waers",
                "genug",
                "mehr faellt mir gerade nicht ein",
                "mehr fÃƒÂ¤llt mir gerade nicht ein",
                "sonst nichts",
                "das wars",
                "das war's",
                "nein",
            )
        )

    @staticmethod
    def _looks_unclear(normalized: str) -> bool:
        return any(
            phrase in normalized
            for phrase in (
                "weiss nicht",
                "nicht genau",
                "unsicher",
                "keine ahnung",
            )
        )

    @staticmethod
    def _looks_negated(normalized: str) -> bool:
        return any(
            phrase in normalized
            for phrase in (
                "habe ich gar nicht",
                "hab ich gar nicht",
                "gar nicht",
                "habe ich nicht",
                "hab ich nicht",
                "das habe ich nicht",
                "das hab ich nicht",
                "nein das habe ich nicht",
                "nein das hab ich nicht",
                "nein, habe ich nicht",
                "nein, hab ich nicht",
            )
        )

    @staticmethod
    def _patch_for_intent(*, question_intent: str | None, value: str) -> ObservationPatch:
        source = Source(source_span=value)
        if question_intent == "duration":
            return ObservationPatch(onset=value, onset_source=source)
        if question_intent in {"description", "free_description"}:
            return ObservationPatch(description=value, description_source=source)
        if question_intent == "localization":
            return ObservationPatch(body_site=value, body_site_source=source)
        if question_intent == "severity":
            return ObservationPatch(severity=value, severity_source=source)
        return ObservationPatch(description=value, description_source=source)

    @staticmethod
    def _resolution_field_keys(resolution: QuestionResolution) -> list[str]:
        keys: list[str] = []
        if resolution.person_update is not None:
            keys.append("person_update")
        if resolution.observation_patch is not None:
            keys.extend(resolution.observation_patch.field_keys())
        if resolution.extra_case_input is not None and (
            resolution.extra_case_input.person is not None
            or resolution.extra_case_input.observations
            or resolution.extra_case_input.topic_entries_to_add
        ):
            keys.append("extra_case_input")
        return keys

    @staticmethod
    def _source(span: str | None) -> Source | None:
        if span in (None, ""):
            return None
        return Source(source_span=span)

    @staticmethod
    def _first_source(normalized: str, phrases: tuple[str, ...]) -> Source | None:
        for phrase in phrases:
            if phrase in normalized or normalized.startswith(phrase):
                return Source(source_span=phrase)
        return None

    @staticmethod
    def _normalize(text: str) -> str:
        normalized = (
            text.casefold()
            .replace("\u00e4", "ae")
            .replace("\u00f6", "oe")
            .replace("\u00fc", "ue")
            .replace("\u00df", "ss")
            .replace("\u00c3\u00a4", "ae")
            .replace("\u00c3\u00b6", "oe")
            .replace("\u00c3\u00bc", "ue")
            .replace("\u00c3\u009f", "ss")
        )
        return " ".join(normalized.split())
