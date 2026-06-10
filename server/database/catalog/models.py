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


class SymptomCluster(SQLModel, table=True):
    """
    Reference catalog entry for a normalized Careena symptom cluster.

    A symptom cluster groups different medical and everyday descriptions
    of similar complaints, for example chest pain, dyspnea, dizziness, or abdominal pain.
    """
    __tablename__ = "catalog_symptom_clusters"

    id: Optional[int] = Field(default=None, primary_key=True)

    cluster_key: str = Field(index=True, max_length=120)
    label_de: str = Field(max_length=255)
    description_de: Optional[str] = Field(default=None)

    # Optional broad grouping for later exports, for example respiratory, neurological, injury, skin.
    cluster_group: Optional[str] = Field(default=None, max_length=120)

    # Tracks how far this cluster has been reviewed for Careena use.
    mapping_status: str = Field(default="draft", max_length=80)
    mapping_notes: Optional[str] = Field(default=None)

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ConsultationReasonClusterLink(SQLModel, table=True):
    """
    Link table between STS consultation reasons and Careena symptom clusters.

    One STS consultation reason can map to one or more symptom clusters.
    One symptom cluster can also appear in multiple STS consultation reasons.
    """
    __tablename__ = "catalog_consultation_reason_cluster_links"

    id: Optional[int] = Field(default=None, primary_key=True)

    consultation_reason_id: int = Field(
        foreign_key="catalog_consultation_reasons.id",
        index=True,
    )
    symptom_cluster_id: int = Field(
        foreign_key="catalog_symptom_clusters.id",
        index=True,
    )

    # primary = main cluster, secondary = relevant but not the main complaint group.
    relevance: str = Field(default="primary", max_length=80)

    mapping_status: str = Field(default="draft", max_length=80)
    mapping_notes: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
