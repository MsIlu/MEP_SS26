from uuid import uuid4

from pydantic import Field
from typing import Literal

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.common.types import DialogueTopicStatus, PlannerModule
from careena_pipeline3.models.domain.guided_input import (
    GuidedInputContract,
    GuidedInputMode,
    GuidedInputOption,
)


class StagedFollowupAnswer(PipelineModel):
    requirement_key: str
    raw_text: str
    slot: str | None = None
    focus_observation_id: str | None = None


class PendingFollowup(PipelineModel):
    requirement_key: str
    slot: str
    kind: Literal["requirement", "conflict", "disambiguation"] = "requirement"
    consequence: str | None = None
    focus_observation_id: str | None = None
    focus_label: str | None = None


class PendingDialogueTransition(PipelineModel):
    kind: Literal["recommendation_ready_check"]
    prompt_code: str | None = None
    allowed_actions: list[str] = Field(
        default_factory=lambda: ["request_recommendation", "report_more_information"]
    )

class PendingSafetyClarification(PipelineModel):
    """Open safety clarification that must be answered before normal progression."""

    kind: Literal["red_flag_clarification"] = "red_flag_clarification"
    question_code: str = "raw_red_flag_clarification"
    source_stage: Literal["raw", "extraction", "case"] = "raw"
    
    guided_input: GuidedInputContract = Field(
        default_factory=lambda: GuidedInputContract(
            mode=GuidedInputMode.STRUCTURED_REQUIRED,
            free_text_allowed=False,
            options=[
                GuidedInputOption(
                    code="yes",
                    label="Ja",
                    effect_code="confirms_red_flag",
                ),
                GuidedInputOption(
                    code="no",
                    label="Nein",
                    effect_code="clears_red_flag",
                ),
                GuidedInputOption(
                    code="unsure",
                    label="Ich bin unsicher",
                    effect_code="keeps_clarification_open",
                ),
                GuidedInputOption(
                    code="immediate_help",
                    label="Ich brauche sofort Hilfe",
                    effect_code="confirms_emergency",
                ),
            ],
        )
    )
    
    evidence_terms: list[str] = Field(default_factory=list)
    focus_observation_id: str | None = None

class DialogueState(PipelineModel):
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    active_case_id: str | None = None
    current_topic_status: DialogueTopicStatus = "single_topic"
    active_modules: list[str] = Field(default_factory=list)
    open_requirements: list[str] = Field(default_factory=list)
    resolved_requirements: list[str] = Field(default_factory=list)
    pending_followup: PendingFollowup | None = None
    pending_dialogue_transition: PendingDialogueTransition | None = None
    pending_safety_clarification: PendingSafetyClarification | None = None
    recommendation_requested: bool = False
    recommendation_ready: bool = False
    recommended_modules: list[PlannerModule] = Field(default_factory=list)
    focus_observation_id: str | None = None
    focus_label: str | None = None
