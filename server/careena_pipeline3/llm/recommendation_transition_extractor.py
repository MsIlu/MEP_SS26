import json

from careena_pipeline3.core.engine import ExtractionEngine
from careena_pipeline3.llm.call_control import CallModelConfig, NEXT_STEP_CALL
from careena_pipeline3.llm.context import build_recommendation_transition_input
from careena_pipeline3.llm.prompts.recommendation_transition import (
    RECOMMENDATION_TRANSITION_SYSTEM_PROMPT,
)
from careena_pipeline3.models.domain import PendingChoicePrompt
from careena_pipeline3.models.workflow import RecommendationTransitionResolution


class LLMRecommendationChoiceExtractor:
    """Small support-call normalizer for open recommendation choice replies."""

    def __init__(
        self,
        engine: ExtractionEngine,
        call_models: CallModelConfig | None = None,
    ):
        self.engine = engine
        self.call_models = call_models

    def resolve(
        self,
        text: str,
        *,
        pending_choice_prompt: PendingChoicePrompt,
        transition_history_messages: list[dict[str, str]] | None = None,
    ) -> RecommendationTransitionResolution:
        payload = build_recommendation_transition_input(
            latest_user_message=text,
            pending_choice_prompt=pending_choice_prompt,
            history_messages=transition_history_messages,
        )
        return self.engine.extract(
            text=json.dumps(payload, ensure_ascii=False),
            system_prompt=RECOMMENDATION_TRANSITION_SYSTEM_PROMPT,
            output_schema=RecommendationTransitionResolution,
            max_tokens=250,
            model=(
                self.call_models.model_for(NEXT_STEP_CALL)
                if self.call_models is not None
                else None
            ),
        )
