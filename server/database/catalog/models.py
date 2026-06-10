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

class ConsultationReasonAssessmentCriterion(SQLModel, table=True):
    """
    Assessment criterion linked to one STS consultation reason.

    This table stores structured, reviewable medical assessment features
    derived from the STS consultation reason context. It does not make
    runtime triage decisions by itself.
    """
    __tablename__ = "catalog_consultation_reason_assessment_criteria"

    id: Optional[int] = Field(default=None, primary_key=True)

    consultation_reason_id: int = Field(
        foreign_key="catalog_consultation_reasons.id",
        index=True,
    )

    criterion_key: str = Field(index=True, max_length=160)
    label_de: str = Field(max_length=255)
    description_de: Optional[str] = Field(default=None)

    # Examples: symptom, observation, duration, severity, onset, risk_factor, vital_sign, context.
    criterion_type: str = Field(max_length=80)

    # User-facing question texts by language, for example {"de": "...", "en": "..."}.
    question_texts_json: str = Field(default="{}")

    # Everyday expressions by language, for example {"de": ["Luftnot"], "en": ["shortness of breath"]}.
    lay_terms_json: str = Field(default="{}")

    # Examples: yes_no, free_text, number, duration, choice, observed_sign.
    expected_answer_type: str = Field(default="yes_no", max_length=80)

    # Safety relevance means the criterion may influence safety clarification or urgency checks.
    is_safety_relevant: bool = Field(default=False)

    # Red flag candidate means this criterion may become a red flag after validation.
    is_red_flag_candidate: bool = Field(default=False)

    # Defines whether this can be self-reported, observed by others, or both.
    observation_context: str = Field(default="self_report_or_observed", max_length=80)

    # Source traceability for review, for example STS wording or internal mapping notes.
    source_note: Optional[str] = Field(default=None)

    mapping_status: str = Field(default="draft", max_length=80)
    mapping_notes: Optional[str] = Field(default=None)

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
