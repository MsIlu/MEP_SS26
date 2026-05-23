from pydantic import Field

from ..base.audit import AuditInfo
from ..base.base import BaseSchema

"""
Data model for recommendation results of a conversation

:param urgency:     
:param recommended_level_of_care:
:param reasoning:
:param confidence:
:param audit:
"""

class Recommendation(BaseSchema):
    urgency: str | None = None

    recommended_level_of_care: str | None = None

    reasoning: str | None = None

    confidence: float | None = None

    audit: AuditInfo = Field(default_factory=AuditInfo)