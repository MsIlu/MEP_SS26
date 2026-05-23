from uuid import uuid4
from pydantic import Field

from .base import BaseSchema, AuditInfo


class RiskFactor(BaseSchema):
    risk_factor_id: str = Field(default_factory=lambda: str(uuid4()))

    name: str

    value: str | None = None

    audit: AuditInfo = Field(default_factory=AuditInfo)