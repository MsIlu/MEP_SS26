from uuid import uuid4
from pydantic import Field

from ..base.base import BaseSchema, AuditInfo

"""
Data model for patient reported allergies 

:param allergy_id:  unique id
:param substance:   Substance 
:param reaction:    described reaction
:param severity:    severity rating
:param audit:       audit information
"""

class Allergy(BaseSchema):
    allergy_id: str = Field(default_factory=lambda: str(uuid4()))

    substance: str

    reaction: str | None = None

    severity: str | None = None

    audit: AuditInfo = Field(default_factory=AuditInfo)