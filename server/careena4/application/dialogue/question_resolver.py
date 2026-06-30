from __future__ import annotations

import re

from careena4.application.dialogue.safety_clarification_resolver import SafetyClarificationResolver
from careena4.core.engine import ExtractionEngine
from careena4.llm.call_control import CallModelConfig, FOLLOWUP_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import ActiveQuestion, Source
from careena4.models.turn import ObservationPatch, PersonUpdate, QuestionResolution
from careena4.server_log import log_event


class QuestionResolver:
    def __init__(
        self,
        *,
        safety_clarification_resolver: SafetyClarificationResolver | None = None,
        extraction_engine: ExtractionEngine | None = None,
        call_model_config: CallModelConfig | None = None,
    ):
        self.safety_clarification_resolver = safety_clarification_resolver or SafetyClarificationResolver()
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
        if question.kind == "person_clarification":
            return self._resolve_without_llm(
                question=question,
                message=message,
                normalized=normalized,
                stripped=stripped,
            )

        llm_result = self._resolve_with_llm(
            question=question,
            message=message,
            history_messages=history_messages,
        )
        if llm_result is not None:
            return llm_result
        return self.normalize_resolution(
            question=question,
            resolution=self._resolve_without_llm(
                question=question,
                message=message,
                normalized=normalized,
                stripped=stripped,
            ),
        )

    def normalize_resolution(
        self,
        *,
        question: ActiveQuestion,
        resolution: QuestionResolution,
    ) -> QuestionResolution:
        return self._validate_resolution(
            question=question,
            resolution=self._canonicalize_resolution(
                question=question,
                resolution=resolution,
            ),
        )

    def _resolve_without_llm(
        self,
        *,
        question: ActiveQuestion,
        message: str,
        normalized: str,
        stripped: str,
    ) -> QuestionResolution:
        if question.kind == "person_clarification":
            def _observation_person_patch(relation: str, source: Source | None) -> ObservationPatch:
                return ObservationPatch(person_ref=relation, person_ref_source=source)

            if question.question_intent == "person_age":
                age_match = re.search(r"\b(\d{1,3})\b", normalized)
                if age_match is None:
                    return QuestionResolution(
                        status="unclear",
                        answer_kind="unclear",
                        trace_notes=["person_age:unclear"],
                    )
                age_value = int(age_match.group(1))
                return QuestionResolution(
                    status="resolved",
                    answer_kind="person_age_provided",
                    clear_active_question=True,
                    resolved_followup_id=question.target_followup_id,
                    person_update=PersonUpdate(
                        age=age_value,
                        age_source=Source(source_span=age_match.group(1)),
                    ),
                    additional_medical_information=self._contains_additional_medical_info(normalized),
                    extra_case_input=None,
                )

            if question.question_intent == "person_sex":
                sex_value = self._sex_from_message(normalized)
                if sex_value is None:
                    return QuestionResolution(
                        status="unclear",
                        answer_kind="unclear",
                        trace_notes=["person_sex:unclear"],
                    )
                return QuestionResolution(
                    status="resolved",
                    answer_kind="person_sex_provided",
                    clear_active_question=True,
                    resolved_followup_id=question.target_followup_id,
                    person_update=PersonUpdate(
                        sex=sex_value,
                        sex_source=Source(source_span=stripped),
                    ),
                    additional_medical_information=self._contains_additional_medical_info(normalized),
                    extra_case_input=None,
                )

            if "kind" in normalized or "sohn" in normalized or "tochter" in normalized:
                source = self._first_source(normalized, ("kind", "sohn", "tochter"))
                return QuestionResolution(
                    status="resolved",
                    answer_kind="person_child",
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
                    extra_case_input=None,
                )
            if "andere" in normalized or "mutter" in normalized or "vater" in normalized:
                source = self._first_source(normalized, ("andere", "mutter", "vater"))
                return QuestionResolution(
                    status="resolved",
                    answer_kind="person_other",
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
                    extra_case_input=None,
                )
            self_terms = ("ich", "selbst", "mich")
            if any(term in normalized for term in self_terms) or normalized.strip() in {
                "ja", "jo", "ja bitte", "ja klar", "ja genau", "yes",
            }:
                source = self._first_source(normalized, self_terms)
                return QuestionResolution(
                    status="resolved",
                    answer_kind="person_self",
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
                    extra_case_input=None,
                )
            return QuestionResolution(
                status="unclear",
                answer_kind="unclear",
                trace_notes=["person_clarification:unclear"],
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

        answer_kind = {
            "duration": "duration_provided",
            "description": "description_provided",
            "severity": "severity_provided",
            "free_description": "free_description_provided",
        }.get(question.question_intent, "resolved")
        return QuestionResolution(
            status="resolved",
            answer_kind=answer_kind,
            clear_active_question=True,
            resolved_followup_id=question.target_followup_id,
            observation_patch=self._patch_for_intent(
                question_intent=question.question_intent,
                value=stripped,
            ),
            additional_medical_information=False,
            extra_case_input=None,
            trace_notes=[f"followup:resolved:{question.question_intent or 'generic'}"],
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

        result = self.normalize_resolution(question=question, resolution=result)

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
        if resolution.answer_kind in {None, ""}:
            return QuestionResolution(
                status="invalid",
                answer_kind="invalid",
                clear_active_question=False,
                trace_notes=["followup:invalid_missing_answer_kind"],
            )

        if question.kind == "person_clarification":
            return self._validate_person_resolution(question=question, resolution=resolution)
        if question.kind != "followup":
            return resolution
        return self._validate_followup_resolution(question=question, resolution=resolution)

    def _validate_person_resolution(
        self,
        *,
        question: ActiveQuestion,
        resolution: QuestionResolution,
    ) -> QuestionResolution:
        if resolution.answer_kind in {"unclear", "invalid"}:
            resolution.status = resolution.answer_kind
            resolution.clear_active_question = False
            return resolution

        if question.question_intent == "person_age":
            if resolution.answer_kind != "person_age_provided":
                return QuestionResolution(
                    status="invalid",
                    answer_kind="invalid",
                    clear_active_question=False,
                    trace_notes=[f"followup:invalid_answer_kind:{resolution.answer_kind}"],
                )
            if resolution.person_update is None or resolution.person_update.age is None:
                return QuestionResolution(
                    status="invalid",
                    answer_kind="invalid",
                    clear_active_question=False,
                    trace_notes=["followup:missing_expected_attribute:person_age"],
                )
            return resolution

        if question.question_intent == "person_sex":
            if resolution.answer_kind != "person_sex_provided":
                return QuestionResolution(
                    status="invalid",
                    answer_kind="invalid",
                    clear_active_question=False,
                    trace_notes=[f"followup:invalid_answer_kind:{resolution.answer_kind}"],
                )
            if resolution.person_update is None or resolution.person_update.sex in (None, ""):
                return QuestionResolution(
                    status="invalid",
                    answer_kind="invalid",
                    clear_active_question=False,
                    trace_notes=["followup:missing_expected_attribute:person_sex"],
                )
            return resolution

        expected_relation = {
            "person_self": "self",
            "person_child": "child",
            "person_other": "other",
        }.get(resolution.answer_kind)
        if expected_relation is None:
            return QuestionResolution(
                status="invalid",
                answer_kind="invalid",
                clear_active_question=False,
                trace_notes=[f"followup:invalid_answer_kind:{resolution.answer_kind}"],
            )
        if question.target_observation_id is not None:
            if resolution.observation_patch is None or resolution.observation_patch.person_ref != expected_relation:
                return QuestionResolution(
                    status="invalid",
                    answer_kind="invalid",
                    clear_active_question=False,
                    trace_notes=["followup:missing_expected_attribute:person_ref"],
                )
            return resolution
        if resolution.person_update is None or resolution.person_update.relation != expected_relation:
            return QuestionResolution(
                status="invalid",
                answer_kind="invalid",
                clear_active_question=False,
                trace_notes=["followup:missing_expected_attribute:person_relation"],
            )
        return resolution

    def _validate_followup_resolution(
        self,
        *,
        question: ActiveQuestion,
        resolution: QuestionResolution,
    ) -> QuestionResolution:
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
            "free_description": "description",
        }.get(question.question_intent)
        allowed_answer_kinds = {
            "duration": {"duration_provided", "duration_plus_more", "negated", "unclear", "invalid"},
            "description": {"description_provided", "description_plus_more", "negated", "unclear", "invalid"},
            "severity": {"severity_provided", "severity_plus_more", "negated", "unclear", "invalid"},
            "free_description": {"free_description_provided", "free_description_plus_more", "negated", "unclear", "invalid"},
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

    @staticmethod
    def _contains_additional_medical_info(normalized: str) -> bool:
        return bool(
            re.search(
                r"\b(schmerz|weh|zieht|stech|dumpf|druck|fieber|husten|atem|sturz|fahrradsturz|verletzt|arzt|uebel|erbrechen|durchfall|hueft|kopf|bauch|brust|hals|bein|arm|leiste)\b",
                normalized,
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

    _GERMAN_DIGITS = {
        "eins": "1", "ein": "1", "eine": "1",
        "zwei": "2",
        "drei": "3",
        "vier": "4",
        "fünf": "5", "fuenf": "5",
        "sechs": "6",
        "sieben": "7",
        "acht": "8",
        "neun": "9",
        "zehn": "10",
    }

    @classmethod
    def _patch_for_intent(cls, *, question_intent: str | None, value: str) -> ObservationPatch:
        source = Source(source_span=value)
        if question_intent == "duration":
            return ObservationPatch(onset=value, onset_source=source)
        if question_intent in {"description", "free_description"}:
            return ObservationPatch(description=value, description_source=source)
        if question_intent == "severity":
            normalized = cls._GERMAN_DIGITS.get(value.strip().casefold(), value)
            return ObservationPatch(severity=normalized, severity_source=source)
        return ObservationPatch(description=value, description_source=source)

    @staticmethod
    def _sex_from_message(normalized: str) -> str | None:
        if any(token in normalized for token in ("weiblich", "frau", "maedchen", "mädchen")):
            return "female"
        if any(token in normalized for token in ("maennlich", "männlich", "mann", "junge")):
            return "male"
        if any(token in normalized for token in ("divers", "nonbinaer", "non-binaer", "nonbinär", "non-binär")):
            return "diverse"
        return None

    @staticmethod
    def _resolution_field_keys(resolution: QuestionResolution) -> list[str]:
        keys: list[str] = []
        if resolution.person_update is not None:
            keys.append("person_update")
        if resolution.observation_patch is not None:
            keys.extend(resolution.observation_patch.field_keys())
        if resolution.extra_case_input is not None and (
            resolution.extra_case_input.has_topic_update()
            or resolution.extra_case_input.person is not None
            or resolution.extra_case_input.observations
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
