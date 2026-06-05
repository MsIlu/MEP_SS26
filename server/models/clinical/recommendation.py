from pydantic import Field, ConfigDict

from models.base.audit import AuditInfo
from models.base.base import BaseSchema

"""
Data model for recommendation results of a conversation

:param urgency:     
:param recommended_level_of_care:
:param reasoning:
:param confidence:
:param audit:
"""

class Recommendation(BaseSchema):
    """
    Liefert die strukturierten Daten
    zum Steuern der Patientendringlichkeit
    """

    model_config = ConfigDict(validate_assignment=True)

    urgency: str | None = Field(
        default=None,
        description="Die Dringlichkeit der Empfehlung (z. B. 'high', 'medium', 'low')."
    )

    recommended_level_of_care: str | None = Field(
        default=None,
        description="Die empfohlene Versorgungsebene (z. B. 'emergency_room', 'general_practitioner', 'self_care')."
    )

    reasoning: str | None = Field(
        default=None,
        description="Die medizinische oder logische Begründung für diese Empfehlung."
    )

    confidence: float | None = Field(
        default=None,
        description="Das Konfidenzintervall bzw. die statistische Sicherheit des LLMs (z. B. 0.95)."
    )

    audit: AuditInfo = Field(
        default_factory=AuditInfo,
        description="Automatische Zeitstempel und Komponenten-Protokolle für diese Empfehlung."
    )