from __future__ import annotations

from careena_pipeline3.core.exceptions import EmptyLLMResponseError, LLMRequestError
from careena_pipeline3.models.turn import (
    EntryDecision,
    ResponseStrategy,
    TurnContext,
)
from careena_pipeline3.models.workflow import RecommendationResult
from careena_pipeline3.application.services.llm_response_generation_service import (
    LLMResponseGenerationService,
)
from careena_pipeline3.application.services.response_text_builder import (
    ResponseTextBuilder,
)


class ResponseGenerationService:
    """
    Builds final response text from an explicit answer strategy.
    """

    def __init__(
        self,
        *,
        static_text_builder: ResponseTextBuilder | None = None,
        llm_response_generation: LLMResponseGenerationService | None = None,
    ):
        self.static_text_builder = static_text_builder or ResponseTextBuilder()
        self.llm_response_generation = llm_response_generation

    def build(
        self,
        *,
        response_mode: str,
        response_strategy: ResponseStrategy,
        context: TurnContext,
        entry_decision: EntryDecision,
        latest_user_message: str,
        conversation_messages: list[dict[str, str]] | None = None,
        recommendation_result: RecommendationResult | None = None,
    ) -> str:
        if (
            response_strategy.kind in {"llm_continue", "llm_bounded_response"}
            and self.llm_response_generation is not None
        ):
            try:
                return self.llm_response_generation.build(
                    response_strategy=response_strategy,
                    context=context,
                    entry_decision=entry_decision,
                    latest_user_message=latest_user_message,
                    conversation_messages=conversation_messages,
                    recommendation_result=recommendation_result,
                )
            except (EmptyLLMResponseError, LLMRequestError):
                pass

        return self.static_text_builder.build(
            response_mode=response_mode,
            response_strategy=response_strategy,
            context=context,
            entry_decision=entry_decision,
            recommendation_result=recommendation_result,
        )
