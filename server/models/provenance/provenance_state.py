from pydantic import Field

from ..base.base import BaseSchema

"""
Data model to store system operations within a session

:param message_ids:  referenced messages
:param extraction_events:    extraction event history
:param merge_events:     merge event history
"""
class ProvenanceState(BaseSchema):
    message_ids: list[str] = Field(default_factory=list)

    extraction_events: list[str] = Field(default_factory=list)

    merge_events: list[str] = Field(default_factory=list)