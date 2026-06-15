from careena_pipeline3.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline3.llm.recommendation_transition_extractor import (
    LLMRecommendationChoiceExtractor,
)
from careena_pipeline3.models.domain import PendingChoicePrompt
from careena_pipeline3.models.workflow import RecommendationTransitionResolution


class RecommendationChoiceResolutionService:
    """
    Resolves an active recommendation choice prompt into one of its
    two allowed semantic actions.
    """

    def __init__(
        self,
        *,
        extractor: LLMRecommendationChoiceExtractor | None = None,
    ):
        self.extractor = extractor

    def resolve(
        self,
        *,
        text: str,
        pending_choice_prompt: PendingChoicePrompt | None,
        transition_history_messages: list[dict[str, str]] | None = None,
    ) -> RecommendationTransitionResolution | None:
        if pending_choice_prompt is None:
            return None
        if pending_choice_prompt.kind != "recommendation_choice":
            return None

        normalized = text.strip()
        if normalized in {"request_recommendation", "report_more_information"}:
            return RecommendationTransitionResolution(
                action=normalized,  # type: ignore[arg-type]
                trace_notes=["choice_resolution:canonical_action"],
            )

        if self.extractor is None:
            return None

        try:
            return self.extractor.resolve(
                text,
                pending_choice_prompt=pending_choice_prompt,
                transition_history_messages=transition_history_messages,
            )
        except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError):
            return None
