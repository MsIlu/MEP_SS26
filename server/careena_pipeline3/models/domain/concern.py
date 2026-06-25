from __future__ import annotations

from typing import Literal

from pydantic import Field

from careena_pipeline3.models.common import PipelineModel

ConcernPhase = Literal[
    "exploration",
    "clarification",
    "closing_check",
    "recommendation_gate",
]

ConcernInformationSufficiency = Literal[
    "insufficient",
    "tentative",
    "sufficient",
]

ConcernRelation = Literal[
    "same_concern",
    "possible_shift",
    "new_concern",
    "dialogue_only",
    "unclear",
]

ConcernTurnRole = Literal[
    "medical_progress",
    "medical_clarification",
    "dialogue_response",
    "closing_choice",
    "unclear",
]

ConcernAllowedNextStep = Literal[
    "safety_question",
    "out_of_scope",
    "ask_clarifying_question",
    "continue_medical",
    "stay_on_closing_check",
    "allow_recommendation",
    "return_to_medical",
]


class ConcernState(PipelineModel):
    """
    Small transitional concern-layer contract.

    It is intentionally not canonical medical truth and not recommendation
    policy. The state exists to keep the current user concern visible without
    forcing that meaning into `MedicalCase`, `DialogueState`, or `Readiness`.
    """

    summary: str | None = None
    active_concern_id: str | None = None
    status: Literal["open", "exploring", "sufficiently_understood"] = "open"
    phase: ConcernPhase = "exploration"
    information_sufficiency: ConcernInformationSufficiency = "insufficient"
    active_closing_node: str | None = None
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
