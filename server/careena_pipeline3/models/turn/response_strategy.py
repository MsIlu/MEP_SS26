from typing import Literal

from careena_pipeline3.models.common import PipelineModel


ResponseStrategyKind = Literal[
    "static_emergency",
    "static_out_of_scope",
    "static_safety_followup",
    "static_followup",
    "static_cannot_assess",
    "static_recommendation_transition",
    "static_recommendation_placeholder",
    "static_return_to_medical",
    "static_medical_acknowledgement",
    "llm_bounded_response",
    "llm_continue",
]


class ResponseStrategy(PipelineModel):
    """
    Role:
    - explicit answer-strategy contract between late response policy and final
      response generation.

    Input contract:
    - receives only the already chosen strategy kind for the current turn.

    Output contract:
    - lets generation choose between small static wording and a narrower
      LLM-backed conversational path without replacing response policy.

    Does not decide:
    - response policy
    - medical case truth
    - recommendation content

    Transitional:
    - yes; V4 keeps `response_mode` visible while introducing a smaller answer
      strategy layer underneath.
    """

    kind: ResponseStrategyKind = "static_cannot_assess"
