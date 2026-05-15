from pydantic import Field
from ..base.base import BaseSchema

"""
Data model to describe the source of information

:param source_message_id    References original message
:param source_message_index Position in chat
:param extractor_version    Version of extraction logic
:param confidence           Confidence of extraction logic
"""
class Provenance(BaseSchema):
    source_message_id: str | None = None

    source_message_index: int | None = None

    extractor_version: str | None = None

    confidence: float | None = Field(default=None, ge=0.0, le=1.0)