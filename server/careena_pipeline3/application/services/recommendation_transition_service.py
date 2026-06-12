from careena_pipeline3.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline3.llm.recommendation_transition_extractor import (
    LLMRecommendationTransitionExtractor,
)
from careena_pipeline3.models.domain import PendingDialogueTransition
from careena_pipeline3.models.workflow import RecommendationTransitionResolution


class RecommendationTransitionService:
    """
    Resolves an active recommendation-ready transition node into one of its
    two allowed semantic actions.
    """

    def __init__(
        self,
        *,
        extractor: LLMRecommendationTransitionExtractor | None = None,
    ):
        self.extractor = extractor

    def resolve(
        self,
        *,
        text: str,
        pending_transition: PendingDialogueTransition | None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> RecommendationTransitionResolution | None:
        if pending_transition is None:
            return None
        if pending_transition.kind != "recommendation_ready_check":
            return None

        normalized = text.strip()
        if normalized in {"request_recommendation", "report_more_information"}:
            return RecommendationTransitionResolution(
                action=normalized,  # type: ignore[arg-type]
                trace_notes=["transition_resolution:canonical_action"],
            )

        if self.extractor is None:
            return None

        try:
            return self.extractor.resolve(
                text,
                pending_transition=pending_transition,
                conversation_messages=conversation_messages,
            )
        except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError):
            return None
