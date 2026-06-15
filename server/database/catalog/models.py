# Author: Cesca
# Created as part of the central Careena medical catalog implementation.
# This module defines database models for medical reference catalog data.
#
# Important:
# These tables store reference knowledge, not user-specific medical cases,
# chat sessions, or runtime dialogue state.

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """
    Return the current UTC timestamp.

    This avoids deprecated datetime.utcnow() usage and keeps timestamps explicit.
    """
    return datetime.now(timezone.utc)


class ConsultationReason(SQLModel, table=True):
    """
    Reference catalog entry for one STS consultation reason.

    This table stores the STS source index and the first Careena mapping layer.
    It does not store symptoms, markers, red flags, or runtime decisions.
    """
    __tablename__ = "catalog_consultation_reasons"

    id: Optional[int] = Field(default=None, primary_key=True)

    source_system: str = Field(default="STS", max_length=80, index=True)
    source_version: Optional[str] = Field(default=None, max_length=40)
    source_year: Optional[int] = Field(default=None)

    source_id: str = Field(index=True, max_length=40)
    source_category_de: Optional[str] = Field(default=None, max_length=255)
    source_label_de: str = Field(max_length=255)

    # JSON-encoded list of STS urgency levels from the source index, for example "[1, 2, 3]".
    # These levels are source metadata only and are not used as direct Careena decisions.
    source_sts_levels_present_json: str = Field(default="[]")

    careena_key: Optional[str] = Field(default=None, index=True, max_length=120)
    careena_label_de: Optional[str] = Field(default=None, max_length=255)

    # Tracks how far this STS entry has been mapped into the Careena catalog.
    mapping_status: str = Field(default="source_indexed", max_length=80)
    mapping_notes: Optional[str] = Field(default=None)

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

class AssessmentCriterion(SQLModel, table=True):
    """
    Reusable assessment criterion derived from STS-relevant medical concepts.

    This table describes what a criterion is and whether Careena can responsibly
    capture it in a lay-user chat context. It does not link the criterion to a
    specific STS consultation reason by itself.
    """
    __tablename__ = "catalog_assessment_criteria"

    id: Optional[int] = Field(default=None, primary_key=True)

    criterion_key: str = Field(index=True, max_length=160)
    label_de: str = Field(max_length=255)
    description_de: Optional[str] = Field(default=None)

    # Examples: symptom, observation, duration, severity, onset, risk_factor,
    # vital_sign, clinical_exam, diagnostic_test, scale, context.
    criterion_type: str = Field(max_length=80)

    # Suggested user-facing question examples by language, for example {"de": "...", "en": "..."}.
    # These are not fixed runtime prompts; Pipeline3 may generate its own wording.
    suggested_question_texts_json: str = Field(default="{}")

    # Everyday expressions by language, for example {"de": ["Luftnot"], "en": ["shortness of breath"]}.
    lay_terms_json: str = Field(default="{}")

    # Defines which structured value Pipeline3 should try to extract.
    # Examples: boolean, free_text, number, duration, choice, measurement, observed_sign, not_collectable.
    expected_value_type: str = Field(default="free_text", max_length=80)

    # Defines which optional UI/input helper could be suggested.
    # Examples: free_text, yes_no_buttons, scale_0_10, duration_input,
    # measurement_input, choice_buttons, observed_sign_input, none.
    suggested_input_mode: str = Field(default="free_text", max_length=80)

    # Users may still answer in free text even if buttons or structured inputs are suggested.
    free_text_allowed: bool = Field(default=True)

    # Defines whether this can be self-reported, observed by others, or both.
    # Examples: self_report, observed, self_report_or_observed, clinician_assessment.
    observation_context: str = Field(default="self_report_or_observed", max_length=80)

    # Defines whether Careena can responsibly capture this STS-relevant criterion.
    # Examples: usable, conditional, not_usable, not_assessed.
    careena_capture_status: str = Field(default="not_assessed", max_length=80)

    # Defines how the criterion can be captured, if at all.
    # Examples: self_report, observer_report, user_provided_measurement,
    # observer_assisted_scale, clinician_assessment, device_required,
    # lab_required, imaging_required, not_collectable.
    careena_capture_method: str = Field(default="not_assessed", max_length=120)

    # Defines whether Careena may ask for this criterion or only accept it if provided.
    # Examples: ask_actively, ask_if_context_relevant, accept_if_user_provided,
    # do_not_ask, do_not_use.
    careena_use_policy: str = Field(default="not_assessed", max_length=120)

    # Documents why an STS-relevant criterion is only conditionally usable or not usable in Careena.
    # Examples: requires_clinician_assessment, requires_device_measurement,
    # requires_lab_result, requires_imaging, not_reliable_for_layperson,
    # not_suitable_for_self_report.
    capture_limitation_reason: Optional[str] = Field(default=None, max_length=255)

    mapping_status: str = Field(default="draft", max_length=80)
    mapping_notes: Optional[str] = Field(default=None)

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ConsultationReasonAssessmentCriterionLink(SQLModel, table=True):
    """
    Link between one STS consultation reason and one reusable assessment criterion.

    This table stores why a criterion matters in a specific STS consultation
    reason context and how it may later influence Pipeline3 safety/readiness logic.
    It does not store user case data.
    """
    __tablename__ = "catalog_consultation_reason_assessment_criterion_links"

    id: Optional[int] = Field(default=None, primary_key=True)

    consultation_reason_id: int = Field(
        foreign_key="catalog_consultation_reasons.id",
        index=True,
    )
    assessment_criterion_id: int = Field(
        foreign_key="catalog_assessment_criteria.id",
        index=True,
    )

    # Examples: primary, supporting, exclusion, source_only.
    relevance: str = Field(default="supporting", max_length=80)

    # Safety relevance is contextual: the same criterion may be safety-relevant
    # for one consultation reason and only supporting context for another.
    is_safety_relevant: bool = Field(default=False)

    # Red flag candidate means the linked criterion may trigger clarification or
    # validation in this consultation reason context. It is not a direct emergency decision.
    is_red_flag_candidate: bool = Field(default=False)

    # Defines how this criterion may later influence Pipeline3 decisions in this context.
    # Examples: safety_clarification_trigger, structured_safety_validator,
    # readiness_requirement, supporting_context, not_used_for_product_decision.
    careena_decision_role: str = Field(default="supporting_context", max_length=120)

    # Defines the medical modeling role of this criterion within this STS reason.
    # Examples: entry_criterion, level_discriminator, supporting_criterion,
    # anamnesis_context, measurement_if_available, clinical_if_reported,
    # deescalation_guard, interim_care_guidance_trigger.
    criterion_role: str = Field(default="supporting_criterion", max_length=80)

    # Stores the STS urgency levels this link is relevant for, for example [1] or [2, 3].
    target_sts_levels_json: str = Field(default="[]")

    # Describes how this linked criterion affects downstream urgency reasoning.
    # Examples: confirms_emergency, supports_higher_urgency,
    # requires_safety_clarification, blocks_deescalation,
    # supports_observation_if_absent, informs_interim_guidance,
    # supporting_context_only.
    urgency_effect: str = Field(default="supporting_context_only", max_length=120)

    # Optional key for interim care advice triggered by this criterion.
    # Examples: cpr_guidance, dependent_limb_positioning, stable_side_position, none.
    interim_care_guidance_key: str = Field(default="none", max_length=120)

    # Source traceability for review, for example STS wording or internal mapping notes.
    source_note: Optional[str] = Field(default=None)

    mapping_status: str = Field(default="draft", max_length=80)
    mapping_notes: Optional[str] = Field(default=None)

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
