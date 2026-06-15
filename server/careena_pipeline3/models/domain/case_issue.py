from uuid import uuid4
from typing import Literal

from pydantic import Field

from careena_pipeline3.models.common import PipelineModel


"""
Date: 2026-06-08
Last changed: 2026-06-08
Author: workbench@freddy

Short description:
Represents a visible conflict or ambiguity in canonical case truth.
It keeps unresolved case-truth issues explicit instead of silently merging them away.
"""
class CaseIssue(PipelineModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    kind: Literal["conflict", "ambiguity", "deferred_update"]
    status: Literal["active", "resolved"] = "active"
    focus_observation_id: str | None = None
    incoming_observation_label: str | None = None
    incoming_observation_type: str | None = None
    note: str | None = None
