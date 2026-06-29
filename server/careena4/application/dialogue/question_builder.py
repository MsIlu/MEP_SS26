from __future__ import annotations

import re

from careena4.core.client import LLMClient
from careena4.core.exceptions import EmptyLLMResponseError, LLMRequestError
from careena4.llm.call_control import CallModelConfig, QUESTION_RENDERING_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import (
    ActiveQuestion,
    FollowupNeed,
    GuidedInputContract,
    GuidedInputMode,
    GuidedInputOption,
)
from careena4.server_log import log_event


class QuestionBuilder:
    def __init__(
        self,
        *,
        llm_client: LLMClient | None = None,
        call_model_config: CallModelConfig | None = None,
    ):
        self.llm_client = llm_client
        self.call_model_config = call_model_config

    def build_for_need(self, *, need: FollowupNeed, focus_label: str | None = None) -> ActiveQuestion:
        case_focus_label = need.case_focus_label or focus_label
        if need.reason == "subject_unclear":
            question = ActiveQuestion(
                kind="subject_clarification",
                question_intent="subject_clarification",
                target_followup_id=need.followup_id,
                prompt_text="Geht es um Sie selbst, um Ihr Kind oder um eine andere Person?",
                blocking=True,
                allows_additional_medical_info=True,
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label or case_focus_label)
            return question
        if need.reason == "person_ref_missing":
            label = focus_label or case_focus_label or "die Beschwerden"
            question = ActiveQuestion(
                kind="subject_clarification",
                question_intent="subject_clarification",
                target_followup_id=need.followup_id,
                target_observation_id=need.observation_id,
                prompt_text=(
                    f"Betreffen {self._accusative_label(label)} Sie selbst, Ihr Kind oder eine andere Person?"
                ),
                blocking=need.blocking,
                allows_additional_medical_info=True,
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label or case_focus_label)
            return question
        if need.reason == "duration_missing":
            question = ActiveQuestion(
                kind="followup",
                question_intent="duration",
                target_followup_id=need.followup_id,
                target_observation_id=need.observation_id,
                prompt_text=self._duration_prompt(case_focus_label=case_focus_label, fallback_label=focus_label),
                blocking=need.blocking,
                allows_additional_medical_info=True,
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label or case_focus_label)
            return question
        if need.reason == "description_missing":
            question = ActiveQuestion(
                kind="followup",
                question_intent="description",
                target_followup_id=need.followup_id,
                target_observation_id=need.observation_id,
                prompt_text=self._description_prompt(case_focus_label=case_focus_label, fallback_label=focus_label),
                blocking=need.blocking,
                allows_additional_medical_info=True,
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label or case_focus_label)
            return question
        if need.reason == "severity_missing":
            label = case_focus_label or focus_label or "die Beschwerde"
            question = ActiveQuestion(
                kind="followup",
                question_intent="severity",
                target_followup_id=need.followup_id,
                target_observation_id=need.observation_id,
                prompt_text=f"Wie stark sind {self._accusative_label(label)} aktuell?",
                blocking=need.blocking,
                allows_additional_medical_info=True,
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label or case_focus_label)
            return question
        if need.reason == "location_unclear":
            question = ActiveQuestion(
                kind="followup",
                question_intent="localization",
                target_followup_id=need.followup_id,
                target_observation_id=need.observation_id,
                prompt_text="Wo genau spueren Sie das?",
                blocking=need.blocking,
                allows_additional_medical_info=True,
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label or case_focus_label)
            return question
        question = ActiveQuestion(
            kind="followup",
            question_intent="free_description",
            target_followup_id=need.followup_id,
            target_observation_id=need.observation_id,
            prompt_text="Koennen Sie das bitte noch etwas genauer beschreiben?",
            blocking=need.blocking,
            allows_additional_medical_info=True,
        )
        question.prompt_text = self._render_prompt(question=question, focus_label=focus_label or case_focus_label)
        return question

    def build_closing_choice(self) -> ActiveQuestion:
        question = ActiveQuestion(
            kind="closing_choice",
            question_intent="free_description",
            prompt_text="Moechten Sie jetzt eine Versorgungsempfehlung erhalten?",
            blocking=False,
            allows_additional_medical_info=True,
            guided_input=GuidedInputContract(
                mode=GuidedInputMode.STRUCTURED_PREFERRED,
                free_text_allowed=True,
                options=[
                    GuidedInputOption(code="recommendation_now", label="Ja, Empfehlung", effect_code="recommendation_now"),
                    GuidedInputOption(code="add_more_information", label="Nein, weitere Angaben", effect_code="add_more_information"),
                ],
            ),
        )
        question.prompt_text = self._render_prompt(question=question, focus_label=None)
        return question

    def build_additional_information_request(self) -> ActiveQuestion:
        return ActiveQuestion(
            kind="followup",
            question_intent="free_description",
            prompt_text="Welche weiteren Angaben zu Ihren Beschwerden moechten Sie noch hinzufuegen?",
            blocking=False,
            allows_additional_medical_info=True,
        )

    def _render_prompt(self, *, question: ActiveQuestion, focus_label: str | None) -> str:
        if self.llm_client is None or getattr(self.llm_client, "client", None) is None:
            return question.prompt_text
        prompt = load_prompt(QUESTION_RENDERING_CALL)
        try:
            rendered = self.llm_client.complete(
                messages=[
                    {"role": "system", "content": prompt.system_prompt},
                    {
                        "role": "user",
                        "content": self._user_prompt(question=question, focus_label=focus_label),
                    },
                ],
                temperature=0.2,
                max_tokens=80,
                model=self.call_model_config.model_for(QUESTION_RENDERING_CALL) if self.call_model_config is not None else None,
                call_name=QUESTION_RENDERING_CALL,
                prompt_name=prompt.name,
                prompt_version=prompt.version,
            ).strip()
        except (EmptyLLMResponseError, LLMRequestError, Exception) as exc:
            log_event(
                "question.rendering.fallback_used",
                layer="application",
                question_kind=question.kind,
                question_intent=question.question_intent,
                reason=type(exc).__name__,
            )
            return question.prompt_text

        if not rendered:
            return question.prompt_text
        if "?" not in rendered:
            rendered = f"{rendered.rstrip('.!')}?"

        log_event(
            "question.rendering.completed",
            layer="application",
            question_kind=question.kind,
            question_intent=question.question_intent,
        )
        return rendered

    def _duration_prompt(self, *, case_focus_label: str | None, fallback_label: str | None) -> str:
        label = case_focus_label or fallback_label or "die Beschwerden"
        if fallback_label and fallback_label != case_focus_label:
            return f"Seit wann bestehen {self._accusative_label(fallback_label)}?"
        return f"Seit wann bestehen {self._accusative_label(label)}?"

    def _description_prompt(self, *, case_focus_label: str | None, fallback_label: str | None) -> str:
        body_site = self._body_site_from_label(case_focus_label) or self._body_site_from_label(fallback_label)
        if body_site is not None:
            return f"Koennen Sie die Beschwerden {self._body_site_phrase(body_site)} noch etwas genauer beschreiben?"
        label = fallback_label or case_focus_label or "die Beschwerden"
        return f"Koennen Sie {self._accusative_label(label)} bitte etwas genauer beschreiben?"

    @staticmethod
    def _body_site_from_label(label: str | None) -> str | None:
        if not label:
            return None
        normalized = label.casefold()
        for token, body_site in (
            ("huefte", "Huefte"),
            ("hüfte", "Huefte"),
            ("bauch", "Bauch"),
            ("brust", "Brust"),
            ("kopf", "Kopf"),
            ("hals", "Hals"),
            ("bein", "Bein"),
            ("arm", "Arm"),
        ):
            if token in normalized:
                return body_site
        return None

    @staticmethod
    def _body_site_phrase(body_site: str) -> str:
        return {
            "Huefte": "an der Huefte",
            "Brust": "in der Brust",
            "Bauch": "im Bauch",
            "Kopf": "am Kopf",
            "Hals": "im Hals",
            "Bein": "im Bein",
            "Arm": "im Arm",
        }.get(body_site, f"an der {body_site}")

    @staticmethod
    def _accusative_label(label: str) -> str:
        stripped = label.strip()
        if re.match(r"^(die|der|das)\b", stripped.casefold()):
            return stripped
        return f"die {stripped}"

    @staticmethod
    def _user_prompt(*, question: ActiveQuestion, focus_label: str | None) -> str:
        return (
            f"question_kind={question.kind}\n"
            f"question_intent={question.question_intent}\n"
            f"focus_label={focus_label or 'none'}\n"
            f"blocking={question.blocking}\n"
            f"Fallback-Text:\n{question.prompt_text}"
        )
