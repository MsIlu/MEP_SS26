from __future__ import annotations

import re

from careena4.core.client import LLMClient
from careena4.core.exceptions import EmptyLLMResponseError, LLMRequestError
from careena4.llm.call_control import CallModelConfig, QUESTION_RENDERING_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import ActiveQuestion, FollowupNeed
from careena4.models.domain.guided_input import GuidedInputContract, GuidedInputMode, GuidedInputOption
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
        if need.reason == "person_missing":
            question = ActiveQuestion(
                kind="person_clarification",
                question_intent="person_clarification",
                target_followup_id=need.followup_id,
                prompt_text="Geht es um dich selbst, um dein Kind oder um eine andere Person?",
                blocking=True,
                allows_additional_medical_info=True,
                guided_input=self._person_clarification_input(),
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label)
            return question
        if need.reason == "age_missing":
            question = ActiveQuestion(
                kind="person_clarification",
                question_intent="person_age",
                target_followup_id=need.followup_id,
                prompt_text=self._person_age_prompt(person_relation=need.person_relation),
                blocking=need.blocking,
                allows_additional_medical_info=True,
                reply_suggestions=self._age_suggestions(person_relation=need.person_relation),
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label)
            return question
        if need.reason == "sex_missing":
            question = ActiveQuestion(
                kind="person_clarification",
                question_intent="person_sex",
                target_followup_id=need.followup_id,
                prompt_text=self._person_sex_prompt(person_relation=need.person_relation),
                blocking=need.blocking,
                allows_additional_medical_info=True,
                guided_input=self._person_sex_input(),
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label)
            return question
        if need.reason == "pregnancy_status_missing":
            prompt = self._pregnancy_prompt(person_relation=need.person_relation)
            return ActiveQuestion(
                kind="person_clarification",
                question_intent="person_pregnancy",
                target_followup_id=need.followup_id,
                prompt_text=prompt,
                blocking=need.blocking,
                allows_additional_medical_info=True,
                guided_input=GuidedInputContract(
                    mode=GuidedInputMode.STRUCTURED_REQUIRED,
                    free_text_allowed=False,
                    options=[
                        GuidedInputOption(code="possible", label="Ja, möglicherweise"),
                        GuidedInputOption(code="excluded", label="Nein"),
                        GuidedInputOption(code="not_applicable", label="Nicht zutreffend"),
                    ],
                ),
            )
        if need.reason == "person_ref_missing":
            label = focus_label or "die Beschwerden"
            question = ActiveQuestion(
                kind="person_clarification",
                question_intent="person_clarification",
                target_followup_id=need.followup_id,
                target_observation_id=need.observation_id,
                prompt_text=(
                    f"Betreffen {self._accusative_label(label)} dich selbst, dein Kind oder eine andere Person?"
                ),
                blocking=need.blocking,
                allows_additional_medical_info=True,
                guided_input=self._person_clarification_input(),
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label)
            return question
        if need.reason == "duration_missing":
            question = ActiveQuestion(
                kind="followup",
                question_intent="duration",
                target_followup_id=need.followup_id,
                target_observation_id=need.observation_id,
                prompt_text=self._duration_prompt(focus_label=focus_label),
                blocking=need.blocking,
                allows_additional_medical_info=True,
                reply_suggestions=["Seit heute", "Seit gestern", "Seit ein paar Tagen", "Seit ca. einer Woche", "Schon länger", "Weiß nicht"],
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label)
            return question
        if need.reason == "description_missing":
            question = ActiveQuestion(
                kind="followup",
                question_intent="description",
                target_followup_id=need.followup_id,
                target_observation_id=need.observation_id,
                prompt_text=self._description_prompt(focus_label=focus_label),
                blocking=need.blocking,
                allows_additional_medical_info=True,
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label)
            return question
        if need.reason == "severity_missing":
            label = focus_label or "die Beschwerde"
            question = ActiveQuestion(
                kind="followup",
                question_intent="severity",
                target_followup_id=need.followup_id,
                target_observation_id=need.observation_id,
                prompt_text=f"Wie stark sind {self._accusative_label(label)} aktuell auf einer Skala von 1 bis 10?",
                blocking=need.blocking,
                allows_additional_medical_info=True,
                guided_input=self._severity_input(),
            )
            question.prompt_text = self._render_prompt(question=question, focus_label=focus_label)
            return question
        question = ActiveQuestion(
            kind="followup",
            question_intent="free_description",
            target_followup_id=need.followup_id,
            target_observation_id=need.observation_id,
            prompt_text="Kannst du das bitte noch etwas genauer beschreiben?",
            blocking=need.blocking,
            allows_additional_medical_info=True,
        )
        question.prompt_text = self._render_prompt(question=question, focus_label=focus_label)
        return question

    @staticmethod
    def _severity_input() -> GuidedInputContract:
        options = [GuidedInputOption(code=str(i), label=str(i)) for i in range(1, 11)]
        options.append(GuidedInputOption(code="unknown", label="Weiß nicht"))
        return GuidedInputContract(
            mode=GuidedInputMode.STRUCTURED_REQUIRED,
            free_text_allowed=False,
            options=options,
        )

    @staticmethod
    def _person_clarification_input() -> GuidedInputContract:
        return GuidedInputContract(
            mode=GuidedInputMode.STRUCTURED_REQUIRED,
            free_text_allowed=False,
            options=[
                GuidedInputOption(code="self", label="Ich selbst"),
                GuidedInputOption(code="child", label="Mein Kind"),
                GuidedInputOption(code="other", label="Jemand anderes"),
            ],
        )

    @staticmethod
    def _person_sex_input() -> GuidedInputContract:
        return GuidedInputContract(
            mode=GuidedInputMode.STRUCTURED_REQUIRED,
            free_text_allowed=False,
            options=[
                GuidedInputOption(code="female", label="Weiblich"),
                GuidedInputOption(code="male", label="Männlich"),
                GuidedInputOption(code="diverse", label="Divers"),
            ],
        )

    @staticmethod
    def _age_suggestions(*, person_relation: str | None) -> list[str]:
        if person_relation == "child":
            return ["Säugling (0–1)", "Kleinkind (2–5)", "Kind (6–12)", "Jugendliche/r (13–17)"]
        return ["Unter 18", "18–30", "31–50", "51–70", "Über 70"]

    def build_additional_information_request(self) -> ActiveQuestion:
        return ActiveQuestion(
            kind="followup",
            question_intent="free_description",
            prompt_text="Welche weiteren Angaben zu deinen Beschwerden moechtest du noch hinzufuegen?",
            blocking=False,
            allows_additional_medical_info=True,
        )

    def _render_prompt(self, *, question: ActiveQuestion, focus_label: str | None) -> str:
        # Skip LLM rendering for click-only questions — the fallback text is concise
        # and the LLM would otherwise add unnecessary "Bitte antworte mit: ..." instructions.
        if question.guided_input is not None and question.guided_input.mode == GuidedInputMode.STRUCTURED_REQUIRED:
            return question.prompt_text
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

    def _duration_prompt(self, *, focus_label: str | None) -> str:
        label = focus_label or "die Beschwerden"
        return f"Seit wann bestehen {self._accusative_label(label)}?"

    def _description_prompt(self, *, focus_label: str | None) -> str:
        label = focus_label or "die Beschwerden"
        return f"Kannst du {self._accusative_label(label)} bitte etwas genauer beschreiben?"

    @staticmethod
    def _person_age_prompt(*, person_relation: str | None) -> str:
        if person_relation == "self":
            return "Wie alt bist du?"
        if person_relation == "child":
            return "Wie alt ist dein Kind?"
        if person_relation == "other":
            return "Wie alt ist die betroffene Person?"
        return "Wie alt ist die betroffene Person?"

    @staticmethod
    def _person_sex_prompt(*, person_relation: str | None) -> str:
        if person_relation == "self":
            return "Welches Geschlecht hast du?"
        if person_relation == "child":
            return "Welches Geschlecht hat dein Kind?"
        if person_relation == "other":
            return "Welches Geschlecht hat die betroffene Person?"
        return "Welches Geschlecht hat die betroffene Person?"

    @staticmethod
    def _pregnancy_prompt(*, person_relation: str | None) -> str:
        if person_relation == "self":
            return "Könnte es sein, dass du derzeit schwanger bist?"
        if person_relation == "child":
            return "Könnte es sein, dass dein Kind derzeit schwanger ist?"
        return "Könnte es sein, dass die Person derzeit schwanger ist?"

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
