from __future__ import annotations

from careena4.core.client import LLMClient
from careena4.core.exceptions import EmptyLLMResponseError, LLMRequestError
from careena4.domain.case import CaseManager
from careena4.llm.call_control import CallModelConfig, RECOMMENDATION_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import ActiveQuestion, ConversationState, MedicalCase
from careena4.models.domain.guided_input import GuidedInputMode
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
        medical_case: MedicalCase | None = None,
        conversation_state: ConversationState | None = None,
        response_history_messages: list[dict[str, str]] | None = None,
        latest_user_message: str | None = None,
        resolved_question: ActiveQuestion | None = None,
    ) -> str:
        if decision.response_mode == "emergency":
            return (
                "Wichtiger Hinweis:\n"
                "Deine Angaben können auf eine akute Notfallsituation hindeuten.\n\n"
                "Bitte wähle sofort den Notruf 112 oder hole umgehend medizinische Hilfe."
            )
        if decision.response_mode == "out_of_scope":
            return "Ich kann hier nur bei gesundheitsbezogenen Anliegen helfen. Bitte beschreibe eine gesundheitliche Beschwerde oder Frage."
        if decision.response_mode in {"ask_safety_question", "ask_followup"} and active_question is not None:
            if (
                active_question.guided_input is not None
                and active_question.guided_input.options
                and active_question.guided_input.mode != GuidedInputMode.STRUCTURED_REQUIRED
            ):
                options = ", ".join(option.label for option in active_question.guided_input.options)
                return f"{active_question.prompt_text} Bitte antworte mit: {options}."
            return active_question.prompt_text
        if decision.response_mode == "guide_next_step":
            return (
                "Es liegen ausreichend Angaben für eine Handlungsempfehlung vor. "
                "Wenn du eine Handlungsempfehlung möchtest, nutze bitte den Empfehlungs-Button."
            )
        if decision.response_mode == "recommend" and recommendation_result is not None:
            return self._render_recommendation(recommendation_result=recommendation_result)
        return "Bitte beschreibe dein gesundheitliches Anliegen genauer."

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
            f"Nächster Schritt: {recommendation_result.next_step}\n\n"
            "Hinweis: Diese Orientierung ersetzt keine ärztliche Untersuchung oder Diagnose."
        )
