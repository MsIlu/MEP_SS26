from pydantic import Field, ConfigDict
from models.base.base import BaseSchema

"""
Erfasst biologische und medizinisch relevante Patientendaten 
"""
class Demographics(BaseSchema):
    model_config = ConfigDict(validate_assignment=True)

    age: int | None = Field(
        default=None,
        ge=0,
        le=125,
        description="Das Alter des Patienten in Jahren."
    )

    biological_sex: str | None = Field(
        default=None,
        description="Das biologische Geschlecht des Patienten (z. B. 'male', 'female', 'other')."
    )

    pregnancy_status: bool | None = Field(
        default=None,
        description="Gibt an, ob aktuell eine Schwangerschaft vorliegt (klinisch kritischer Faktor)."
    )