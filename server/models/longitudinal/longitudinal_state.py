from pydantic import Field, ConfigDict
from models.base.base import BaseSchema

"""
Verwaltet die Langzeitdaten und Verlaufsbeobachtung eines Patienten
über mehrere Chat-Sessions hinweg.

Parameter sind noch nicht final
"""
class LongitudinalState(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    recurring_symptoms: list[str] = Field(
        default_factory=list,
        description="Liste historisch wiederkehrender Symptome des Patienten (z. B. 'chronische Migräne')."
    )

    frequent_visit_patterns: list[str] = Field(
        default_factory=list,
        description="Analysierte Nutzungsmuster oder zeitliche Häufungen der App-Inanspruchnahme."
    )

    derived_risk_patterns: list[str] = Field(
        default_factory=list,
        description="Vom System oder LLM abgeleitete klinische Risikofaktoren basierend auf der Historie."
    )