from uuid import uuid4
from pydantic import Field, ConfigDict

from models.base.base import BaseSchema 
from models.base.audit import AuditInfo
from models.provenance.provenance_state import ProvenanceState


class ClinicalFact(BaseSchema):
    """
    Hält den noch unfertigen Patienten-Eintrag sowie die medizinisch normalisierte Form
    
    """
    model_config = ConfigDict(validate_assignment=True)

    fact_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Eindeutige, automatisch generierte ID des klinischen Faktums."
    )

    fact_type: str = Field(
        ...,
        description="Der Typ des Faktums (z. B. 'Symptom', 'Medikation', 'Diagnose')."
    )

    value: str = Field(
        ...,
        description="Der originale Text- oder Zahlenwert aus dem Patienten-Chat."
    )

    normalized_value: str | None = Field(
        default=None,
        description="Der medizinisch standardisierte Begriff (z. B. SNOMED-CT / ICD-10 Analogon)."
    )

    provenance: ProvenanceState = Field(
        default_factory=ProvenanceState,
        description="Herkunftsnachweis (Provenance), der den Fakt mit einer spezifischen Nachricht verknüpft."
    )

    audit: AuditInfo = Field(
        default_factory=AuditInfo,
        description="Automatische Zeitstempel und Komponenten-Protokolle für diesen Fakt."
    )