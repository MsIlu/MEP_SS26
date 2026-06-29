from __future__ import annotations

import re

from careena4.core.engine import ExtractionEngine
from careena4.domain.case import CaseManager
from careena4.llm.call_control import CallModelConfig, ENTRY_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import ActiveQuestion, MedicalCase
from careena4.models.turn import EntryAssessment
from careena4.server_log import log_event


class EntryClassifier:
    _MEDICAL_HINTS = (
        "schmerz",
        "fieber",
        "husten",
        "atem",
        "luft",
        "sturz",
        "gefallen",
        "verletz",
        "uebel",
        "uebelkeit",
        "erbrechen",
        "durchfall",
        "schwindel",
        "kopf",
        "bauch",
        "brust",
        "huefte",
        "bein",
        "arm",
        "blut",
    )
    _OUT_OF_SCOPE_HINTS = ("wetter", "programm", "code", "urlaub", "finanzen", "schule")

    def __init__(
        self,
        *,
        extraction_engine: ExtractionEngine | None = None,
        call_model_config: CallModelConfig | None = None,
        case_manager: CaseManager | None = None,
    ):
        self.extraction_engine = extraction_engine
        self.call_model_config = call_model_config
        self.case_manager = case_manager or CaseManager()

    def classify(
        self,
        *,
        message: str,
        active_question: ActiveQuestion | None = None,
        medical_case: MedicalCase | None = None,
        history_messages: list[dict[str, str]] | None = None,
    ) -> EntryAssessment:
        llm_result = self._classify_with_llm(
            message=message,
            active_question=active_question,
            medical_case=medical_case,
            history_messages=history_messages,
        )
        if llm_result is not None:
            return llm_result
        return self._heuristic_classify(
            message=message,
            active_question=active_question,
            medical_case=medical_case,
        )

    def _classify_with_llm(
        self,
        *,
        message: str,
        active_question: ActiveQuestion | None,
        medical_case: MedicalCase | None,
        history_messages: list[dict[str, str]] | None,
    ) -> EntryAssessment | None:
        if self.extraction_engine is None:
            return None
        prompt = load_prompt(ENTRY_CALL)
        try:
            result = self.extraction_engine.extract(
                text=self._build_user_prompt(
                    message=message,
                    active_question=active_question,
                    medical_case=medical_case,
                    history_messages=history_messages,
                ),
                system_prompt=prompt.system_prompt,
                output_schema=EntryAssessment,
                temperature=0.0,
                max_tokens=220,
                model=self.call_model_config.model_for(ENTRY_CALL) if self.call_model_config is not None else None,
                call_name=ENTRY_CALL,
                prompt_name=prompt.name,
                prompt_version=prompt.version,
            )
        except Exception as exc:
            log_event(
                "entry.classification.fallback_used",
                layer="application",
                reason=type(exc).__name__,
            )
            return None

        if result.answers_active_question and result.message_kind != "question_answer":
            result.message_kind = "question_answer"
        if not result.in_scope:
            result.medical_relevance = "non_medical"
            result.contains_new_medical_information = False
            result.message_kind = "out_of_scope"

        log_event(
            "entry.classification.completed",
            layer="application",
            message_kind=result.message_kind,
            in_scope=result.in_scope,
            answers_active_question=result.answers_active_question,
            contains_new_medical_information=result.contains_new_medical_information,
        )
        return result

    def _heuristic_classify(
        self,
        *,
        message: str,
        active_question: ActiveQuestion | None = None,
        medical_case: MedicalCase | None = None,
    ) -> EntryAssessment:
        stripped = message.strip()
        normalized = self._normalize(stripped)
        in_scope = not any(hint in normalized for hint in self._OUT_OF_SCOPE_HINTS)
        answers_active_question = active_question is not None
        medical_relevance = "medical" if self._looks_medical(normalized) or answers_active_question else "non_medical"
        contains_new_medical_information = self._looks_medical(normalized)
        if not in_scope:
            return EntryAssessment(
                in_scope=False,
                medical_relevance="non_medical",
                answers_active_question=answers_active_question,
                contains_new_medical_information=False,
                message_kind="out_of_scope",
            )
        if answers_active_question:
            return EntryAssessment(
                in_scope=True,
                medical_relevance=medical_relevance,
                answers_active_question=True,
                contains_new_medical_information=contains_new_medical_information,
                message_kind="question_answer",
            )
        has_case_context = medical_case is not None and self.case_manager.has_observations(medical_case=medical_case)
        if contains_new_medical_information and not has_case_context:
            message_kind = "new_case_report"
        elif contains_new_medical_information:
            message_kind = "same_case_update"
        else:
            message_kind = "dialogue_only"
        return EntryAssessment(
            in_scope=True,
            medical_relevance=medical_relevance,
            answers_active_question=False,
            contains_new_medical_information=contains_new_medical_information,
            message_kind=message_kind,
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
        history_text = "\n".join(history_lines[-4:]) if history_lines else "- none"
        active_question_text = (
            f"kind={active_question.kind}; intent={active_question.question_intent}; prompt={active_question.prompt_text}"
            if active_question is not None
            else "none"
        )
        topic_text = self.case_manager.topic_label(medical_case=medical_case) or "none"
        return (
            f"Aktueller Fallfokus: {topic_text}\n"
            f"Offene Frage: {active_question_text}\n"
            f"Letzte Konversation:\n{history_text}\n"
            f"Letzte Nutzernachricht:\n{message}"
        )

    def _looks_medical(self, normalized: str) -> bool:
        if any(hint in normalized for hint in self._MEDICAL_HINTS):
            return True
        return bool(re.search(r"\b(krank|beschwer|symptom|weh)\b", normalized))

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
