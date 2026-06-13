from typing import Literal

from careena_pipeline3.models.common import PipelineModel, ResponseMode


ResponseMedicalState = Literal[
    "followup_required",
    "no_medical_problem",
    "sufficient_information",
]

ResponseTransitionState = Literal[
    "inactive",
    "awaiting_reply",
    "commit_recommendation",
    "return_to_medical",
]

ResponseRecommendationState = Literal[
    "not_requested",
    "requested_not_ready",
    "ready_for_transition",
    "ready_for_recommendation",
]


class ResponseState(PipelineModel):
    """
    Role:
    - small explicit reaction-state kernel for the late turn pipeline.

    Input contract:
    - carries only the minimal late-turn axes needed by response policy:
      safety override, entry hint, medical state, transition state, and
      recommendation state.

    Output contract:
    - gives `ResponseManager` a smaller explicit policy basis than loose
      combinations of booleans and modes.

    Does not decide:
    - final response text
    - recommendation content
    - medical case truth

    Transitional:
    - yes; `response_mode` remains the externally visible path while older
      recommendation/transition semantics still survive underneath as legacy
      observability and future recommendation hooks.
    """

    selected_response_mode: ResponseMode | None = None
    safety_override: ResponseMode | None = None
    entry_response_hint: ResponseMode | None = None
    medical_state: ResponseMedicalState = "sufficient_information"
    # Legacy observability / future recommendation hook.
    transition_state: ResponseTransitionState = "inactive"
    # Legacy observability / future recommendation hook.
    recommendation_state: ResponseRecommendationState = "not_requested"
