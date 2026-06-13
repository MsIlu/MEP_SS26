from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.domain import PendingDialogueTransition
from careena_pipeline3.models.turn.response_state import ResponseState
from careena_pipeline3.models.turn.response_strategy import ResponseStrategy
from careena_pipeline3.models.workflow import RecommendationResult


class ResponsePlan(PipelineModel):
    """
    Role:
    - explicit late-turn response-policy result returned by `ResponseManager`.

    Input contract:
    - receives a small reaction-state kernel plus the chosen visible response
      path and optional payloads.

    Output contract:
    - gives the orchestrator one place to apply late response policy results.

    Does not decide:
    - medical case truth
    - readiness evaluation
    - final recommendation content beyond attached placeholders

    Transitional:
    - yes; `response_mode` remains the outward path while older recommendation
      transition hooks may still be attached as explicit legacy payloads.
    """

    response_mode: str
    response_state: ResponseState = Field(default_factory=ResponseState)
    response_strategy: ResponseStrategy = Field(default_factory=ResponseStrategy)
    response_text: str | None = None
    recommendation_result: RecommendationResult | None = None
    # Legacy recommendation transition hook, not applied by the active
    # pre-recommend routing contract.
    pending_dialogue_transition: PendingDialogueTransition | None = None
    trace_notes: list[str] = Field(default_factory=list)
