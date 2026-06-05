from pydantic import Field, ConfigDict
from models.base.base import BaseSchema

"""
Hält jeden extrahierten klinischen Fakt mit seiner Ursprungsnachricht fest
"""
class Provenance(BaseSchema):

    model_config = ConfigDict(validate_assignment=True)

    source_message_id: str | None = Field(
        default=None,
        description="Referenz-ID der Chat-Nachricht, aus der die Information stammt."
    )

    source_message_index: int | None = Field(
        default=None,
        description="Die exakte Position (Index) der Nachricht innerhalb des Chat-Verlaufs."
    )

    extractor_version: str | None = Field(
        default=None,
        description="Die Version der eingesetzten Extraktions-Logik bzw. des LLM-Prompts."
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Konfidenzwert der Extraktion (Gleitkommazahl von 0.0 bis 1.0)."
    )