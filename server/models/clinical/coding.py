from pydantic import Field, ConfigDict
from models.base.base import BaseSchema

"""
Data structure for standardized medical encoding.
Relevant for ICD, SNOMED, LOINC and FHIR mappings.

:param system   encoding system
:param code     system specific code
:param display  human readable description
"""
class Coding(BaseSchema):
    """
    Ermöglicht die semantische Interoperabilität 
    durch die Abbildung von System, Code und Displaytext. 
    """
    model_config = ConfigDict(validate_assignment=True)

    system: str | None = Field(
        default=None,
        description="Das Codierungssystem als URI (z. B. 'http://hl7.org/fhir/sid/icd-10' oder 'http://snomed.info/sct')."
    )

    code: str | None = Field(
        default=None,
        description="Der spezifische Code aus dem gewählten System (z. B. 'M54.5')."
    )

    display: str | None = Field(
        default=None,
        description="Die für Menschen lesbare Beschreibung des Codes (z. B. 'Kreuzschmerz')."
    )