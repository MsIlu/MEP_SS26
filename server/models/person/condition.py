from uuid import uuid4
from pydantic import Field

from ..base.base import BaseSchema, AuditInfo
from ..provenance.provenance import Coding

"""
Data model for persistant or chronic medical conditions

:param condition_id 
:param name         name of condition
:param coding       encoding of condition
:param chronic      is condition chronic
:param audit        audit information
"""
class Condition(BaseSchema):
    condition_id: str = Field(default_factory=lambda: str(uuid4()))

    name: str

    coding: Coding | None = None

    chronic: bool = True

    audit: AuditInfo = Field(default_factory=AuditInfo)