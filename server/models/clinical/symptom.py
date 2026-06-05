from uuid import uuid4
from pydantic import Field, ConfigDict

from models.base.base import BaseSchema
from models.base.audit import AuditInfo
from models.provenance.provenance_state import ProvenanceState
from models.clinical.coding import Coding
from models.clinical.temporal import TemporalState
from models.clinical.assertion_state import AssertionState


class SymptomAttributes(BaseSchema):
    """
    Die Ausprägung eines Symptoms wird spezifiziert.
    Der Schweregrad, die Lokalisation und Schmerz 
    """
    model_config = ConfigDict(validate_assignment=True)

    severity: int | None = Field(
        default=None, 
        ge=0, 
        le=10,
        description="Schweregrad des Symptoms auf einer numerischen Skala (0 = kein Schmerz, 10 = Maximalschmerz)."
    )

    location: str | None = Field(
        default=None,
        description="Die anatomische Lokalisation des Symptoms (z. B. 'Unterbauch links')."
    )

    radiation: str | None = Field(
        default=None,
        description="Gibt an, ob und wohin das Symptom ausstrahlt (z. B. 'ausstrahlend in den Rücken')."
    )

    frequency: str | None = Field(
        default=None,
        description="Die zeitliche Häufigkeit des Auftretens (z. B. 'kontinuierlich', 'episodisch', 'intermittierend')."
    )

class Symptom(BaseSchema):
    """
    Bündelt alle extrahierten Attribute, zeitlichen Zustände und Kontexte einer Beschwerde
    """
    model_config = ConfigDict(validate_assignment=True)

    symptom_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Eindeutige, automatisch generierte ID des Symptoms."
    )

    raw_text: str = Field(
        ...,
        description="Der originale Textabschnitt aus dem Chat, in dem das Symptom genannt wurde."
    )

    normalized_name: str = Field(
        ...,
        description="Der medizinisch bereinigte Standardname des Symptoms (z. B. 'Cephalgie' für Kopfschmerzen)."
    )

    coding: Coding | None = Field(
        default=None,
        description="Die FHIR-konforme medizinische Codierung (z. B. ICD-10 oder SNOMED-CT)."
    )

    attributes: SymptomAttributes = Field(
        default_factory=SymptomAttributes,
        description="Detaillierte klinische Ausprägungen und Spezifikationen des Symptoms."
    )

    temporal: TemporalState = Field(
        default_factory=TemporalState,
        description="Zeitlicher Verlauf, Beginn und Dauer der Beschwerde."
    )

    assertion: AssertionState = Field(
        default_factory=AssertionState,
        description="Der Aussagekontext (z. B. ob das Symptom verneint oder unsicher ist)."
    )

    status: str = Field(
        default="active",
        description="Der aktuelle Status des Symptoms im Behandlungsverlauf (z. B. 'active', 'resolved')."
    )

    provenance: ProvenanceState = Field(
        default_factory=ProvenanceState,
        description="Herkunftsnachweis, der das Symptom mit der Quellnachricht verknüpft."
    )

    audit: AuditInfo = Field(
        default_factory=AuditInfo,
        description="Automatische Zeitstempel und Komponenten-Protokolle für dieses Symptom."
    )