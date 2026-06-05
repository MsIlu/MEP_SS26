from pydantic import Field, ConfigDict

from models.base.base import BaseSchema

"""
Datenstruktur, um die Konverversation des nicht-medizinischen Chatfluss zu steuern.
"""
class ConversationState(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    current_phase: str = Field(
        default="information_gathering",
        description="Die aktuelle Phase des Gesprächs (z. B. 'information_gathering', 'summary', 'final_assessment')."
    )

    missing_information: list[str] = Field(
        default_factory=list,
        description="Liste noch offener klinischer Datenpunkte, die das LLM erfragen muss."
    )

    pending_questions: list[str] = Field(
        default_factory=list,
        description="Zwischengespeicherte Fragen, die im weiteren Verlauf beantwortet werden müssen."
    )

    summary_ready: bool = Field(
        default=False,
        description="True, wenn das LLM genügend Informationen für eine Zusammenfassung gesammelt hat."
    )

    summary_confirmed: bool = Field(
        default=False,
        description="True, wenn der Patient die vom LLM generierte Zusammenfassung bestätigt hat."
    )

    assessment_complete: bool = Field(
        default=False,
        description="True beendet die Konversation und schließt die Session."
    )