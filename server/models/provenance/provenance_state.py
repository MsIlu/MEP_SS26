from pydantic import Field, ConfigDict
from models.base.base import BaseSchema

"""
Stellt die Audit-Schnittstelle bereit, aus welcher Chatnachricht ein klinischer Fakt oder Symptom generiert wurde.
"""

class ProvenanceState(BaseSchema):
    

    model_config = ConfigDict(validate_assignment=True)

    message_ids: list[str] = Field(
        default_factory=list,
        description="Liste von Referenz-IDs der Chat-Nachrichten, aus denen die Daten extrahiert wurden."
    )

    extraction_events: list[str] = Field(
        default_factory=list,
        description="Historie der Extraktions-Ereignisse (Zeitstempel, Pipeline-IDs, Modell-Versionen)."
    )

    merge_events: list[str] = Field(
        default_factory=list,
        description="Historie der Zusammenführungs-Ereignisse (Merge-Logik bei redundanten Datenpunkten)."
    )