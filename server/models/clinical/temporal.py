"""
Definiert das zeitliche Zustandsschema (Beginn, Dauer, Verlauf, Rhythmus) 
eines Symptoms für die strukturierte klinische Anamnese.
"""

from pydantic import Field, ConfigDict
from models.base.base import BaseSchema


class TemporalState(BaseSchema):
    """
    Ermöglicht dem Backend die chronologische Einordnung von Beschwerden.
    """

    model_config = ConfigDict(validate_assignment=True)

    onset: str | None = Field(
        default=None,
        description="Der Beginn und die Art des Auftretens (z. B. 'akut', 'schleichend', 'vor 3 Tagen')."
    )

    duration: str | None = Field(
        default=None,
        description="Die bisherige Gesamtdauer des Symptoms (z. B. 'seit 2 Wochen')."
    )

    progression: str | None = Field(
        default=None,
        description="Der Verlauf des Symptoms (z. B. 'proredient/verschlimmernd', 'regredient/bessernd', 'stabil')."
    )

    episodic: bool = Field(
        default=True,
        description="True, wenn das Symptom in Schüben oder Anfällen auftritt; False bei Dauerschmerz."
    )

    resolved: bool = Field(
        default=False,
        description="Gibt an, ob das Symptom zum aktuellen Zeitpunkt bereits vollständig abgeklungen ist."
    )