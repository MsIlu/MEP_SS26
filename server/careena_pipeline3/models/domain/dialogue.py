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


class PendingChoicePrompt(PipelineModel):
    """Visible process contract for one open system choice prompt."""

    kind: Literal["recommendation_choice"]
    prompt_code: str | None = None
    allowed_actions: list[str] = Field(
        default_factory=lambda: ["request_recommendation", "report_more_information"]
    )


class PendingSafetyClarification(PipelineModel):
    """Open safety clarification that must be answered before normal progression."""

    kind: Literal["red_flag_clarification"] = "red_flag_clarification"
    question_code: str = "raw_red_flag_clarification"
    source_stage: Literal["raw", "extraction", "case"] = "raw"

    question_text: str | None = None

    # Reference metadata for the catalog criterion that caused this clarification.
    source_system: Literal["STS"] = "STS"
    source_version: str | None = None
    consultation_reason_source_id: str | None = None
    consultation_reason_key: str | None = None
    criterion_key: str | None = None
    criterion_role: str | None = None
    urgency_effect: str | None = None
    catalog_mapping_status: Literal[
        "unmapped",
        "catalog_matched",
        "fallback_no_catalog_match",
    ] = "unmapped"

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
    pending_choice_prompt: PendingChoicePrompt | None = None
    pending_safety_clarification: PendingSafetyClarification | None = None

    # Legacy recommendation intent hook for future recommendation routing.
    recommendation_requested: bool = False
    recommendation_ready: bool = False
    recommended_modules: list[PlannerModule] = Field(default_factory=list)
    focus_observation_id: str | None = None
    focus_label: str | None = None