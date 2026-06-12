from __future__ import annotations

from typing import Literal

from pydantic import Field

from careena_pipeline3.models.common import PipelineModel


class ConcernState(PipelineModel):
    """
    Small transitional concern-layer contract.

    It is intentionally not canonical medical truth and not recommendation
    policy. The state exists to keep the current user concern visible without
    forcing that meaning into `MedicalCase`, `DialogueState`, or `Readiness`.
    """

    summary: str | None = None
    status: Literal["open", "exploring", "sufficiently_understood"] = "open"
    shift_state: Literal["same_concern", "expanded", "shifted", "unclear"] = "unclear"
    last_update_source: (
        Literal[
            "initial_report",
            "followup",
            "user_clarification",
            "system_inference",
        ]
        | None
    ) = None
    linked_observation_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
