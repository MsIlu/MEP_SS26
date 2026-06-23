from __future__ import annotations

from careena4.domain.case import CaseManager
from careena4.core.client import LLMClient
from careena4.core.exceptions import EmptyLLMResponseError, LLMRequestError
from careena4.llm.call_control import CallModelConfig, RECOMMENDATION_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import ActiveQuestion, CaseTopic, ConversationState, MedicalCase
from careena4.models.turn import TurnDecision
from careena4.models.workflow import RecommendationResult
from careena4.server_log import log_event


class ResponseBuilder:
    def __init__(
        self,
        *,
        llm_client: LLMClient | None = None,
        call_model_config: CallModelConfig | None = None,
        case_manager: CaseManager | None = None,
    ):
        self.llm_client = llm_client
        self.call_model_config = call_model_config
        self.case_manager = case_manager or CaseManager()

    def build(
        self,
        *,
        decision: TurnDecision,
        recommendation_result: RecommendationResult | None = None,
        active_question: ActiveQuestion | None = None,
        topic_mismatch: bool = False,
        case_topic: CaseTopic | None = None,
        medical_case: MedicalCase | None = None,
        conversation_state: ConversationState | None = None,
        response_history_messages: list[dict[str, str]] | None = None,
        latest_user_message: str | None = None,
        resolved_question: ActiveQuestion | None = None,
    ) -> str:
        if decision.response_mode == "emergency":
            return (
                "Wichtiger Hinweis:\n"
                "Ihre Angaben koennen auf eine akute Notfallsituation hindeuten.\n\n"
                "Bitte waehlen Sie sofort den Notruf 112 oder holen Sie umgehend medizinische Hilfe."
            )
        if decision.response_mode == "out_of_scope":
            if topic_mismatch:
                return (
                    "Das klingt nach einem neuen gesundheitlichen Anliegen und passt nicht mehr sauber zum aktuellen Fall. "
                    "Bitte starten Sie dafuer am besten eine neue Session oder beschreiben Sie wieder das aktuelle Anliegen."
                )
            return "Ich kann hier nur bei gesundheitsbezogenen Anliegen helfen. Bitte beschreiben Sie eine gesundheitliche Beschwerde oder Frage."
        if decision.response_mode in {"ask_safety_question", "ask_followup", "guide_next_step"} and active_question is not None:
            if active_question.guided_input is not None and active_question.guided_input.options:
                options = ", ".join(option.label for option in active_question.guided_input.options)
                return f"{active_question.prompt_text} Bitte antworten Sie mit: {options}."
            return active_question.prompt_text
        if decision.response_mode == "request_case_description":
            return self._render_case_description_request(
                medical_case=medical_case,
                conversation_state=conversation_state,
            )
        if decision.response_mode == "recommend" and recommendation_result is not None:
            return self._render_recommendation(recommendation_result=recommendation_result)
        return "Bitte beschreiben Sie Ihr gesundheitliches Anliegen genauer."

    def _render_recommendation(self, *, recommendation_result: RecommendationResult) -> str:
        if self.llm_client is None or getattr(self.llm_client, "client", None) is None:
            return self._fallback_recommendation(recommendation_result=recommendation_result)
        prompt = load_prompt(RECOMMENDATION_CALL)
        try:
            rendered = self.llm_client.complete(
                messages=[
                    {"role": "system", "content": prompt.system_prompt},
                    {
                        "role": "user",
                        "content": self._recommendation_user_prompt(recommendation_result=recommendation_result),
                    },
                ],
                temperature=0.2,
                max_tokens=220,
                model=self.call_model_config.model_for(RECOMMENDATION_CALL) if self.call_model_config is not None else None,
                call_name=RECOMMENDATION_CALL,
                prompt_name=prompt.name,
                prompt_version=prompt.version,
            ).strip()
        except (EmptyLLMResponseError, LLMRequestError, Exception) as exc:
            log_event(
                "recommendation.rendering.fallback_used",
                layer="application",
                reason=type(exc).__name__,
            )
            return self._fallback_recommendation(recommendation_result=recommendation_result)

        if not rendered:
            return self._fallback_recommendation(recommendation_result=recommendation_result)

        log_event(
            "recommendation.rendering.completed",
            layer="application",
            urgency=recommendation_result.urgency,
        )
        return rendered

    @staticmethod
    def _recommendation_user_prompt(*, recommendation_result: RecommendationResult) -> str:
        return (
            f"summary={recommendation_result.summary}\n"
            f"reasons={recommendation_result.reasons}\n"
            f"next_step={recommendation_result.next_step}\n"
            f"limitations={recommendation_result.limitations}\n"
            f"urgency={recommendation_result.urgency}\n"
            f"care_level={recommendation_result.care_level}\n"
            f"specialty={recommendation_result.specialty}"
        )

    @staticmethod
    def _fallback_recommendation(*, recommendation_result: RecommendationResult) -> str:
        return (
            f"{recommendation_result.summary}\n\n"
            f"Naechster Schritt: {recommendation_result.next_step}\n\n"
            "Hinweis: Diese Orientierung ersetzt keine aerztliche Untersuchung oder Diagnose."
        )

    def _render_case_description_request(
        self,
        *,
        medical_case: MedicalCase | None,
        conversation_state: ConversationState | None,
    ) -> str:
        if medical_case is not None and self.case_manager.has_active_observations(medical_case=medical_case):
            return "Bitte beschreiben Sie Ihre Beschwerden noch etwas genauer."
        if conversation_state is not None and conversation_state.recommendation_requested:
            return "Damit ich eine Versorgungsempfehlung geben kann, beschreiben Sie bitte Ihr gesundheitliches Anliegen oder Ihre Beschwerden genauer."
        return "Bitte beschreiben Sie Ihr gesundheitliches Anliegen oder Ihre Beschwerden genauer."
