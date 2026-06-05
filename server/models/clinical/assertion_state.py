from pydantic import Field, ConfigDict
from models.base.base import BaseSchema


class AssertionState(BaseSchema):
    """
    Schema zur Erfassung des Aussage-Status eines klinischen Faktums.
    Verhindert, dass verneinte oder hypothetische Symptome als feste Diagnosen missinterpretiert werden.
    """

    model_config = ConfigDict(validate_assignment=True)

    negated: bool = Field(
        default=False,
        description="Gibt an, ob das Symptom explizit verneint wurde (z. B. 'keine Schmerzen')."
    )

    uncertain: bool = Field(
        default=False,
        description="Gibt an, ob die Aussage mit Unsicherheit behaftet ist (z. B. 'vielleicht Fieber')."
    )

    hypothetical: bool = Field(
        default=False,
        description="Gibt an, ob das Symptom rein hypothetisch genannt wurde (z. B. 'falls Schmerzen auftreten')."
    )

    reported_by_patient: bool = Field(
        default=True,
        description="True, wenn der Patient selbst berichtet; False, wenn es z. B. Beobachtungen Dritter sind."
    )