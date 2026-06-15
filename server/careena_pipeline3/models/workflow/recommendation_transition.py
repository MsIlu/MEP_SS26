from typing import Literal

from pydantic import Field

from careena_pipeline3.models.common import PipelineModel


RecommendationTransitionAction = Literal[
    "request_recommendation",
    "report_more_information",
]


class RecommendationTransitionResolution(PipelineModel):
    """Two-way normalization result for an active recommendation transition."""

    action: RecommendationTransitionAction
    trace_notes: list[str] = Field(default_factory=list)
