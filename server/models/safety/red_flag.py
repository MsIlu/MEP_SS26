from uuid import uuid4
from pydantic import Field

from ..base.base import BaseSchema
from ..provenance.provenance import Provenance

"""
Data Model for red flags

*** muss noch mit red flag logik abgestimmt werden

"""
class RedFlag(BaseSchema):
    red_flag_id: str = Field(default_factory=lambda: str(uuid4()))

    rule_id: str

    name: str

    severity: str

    category: str | None = None

    action: str | None = None

    matched_keywords: list[str] = Field(default_factory=list)

    provenance: Provenance = Field(default_factory=Provenance)