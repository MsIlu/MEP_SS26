from ..base import BaseSchema

"""
Data structure for standardized medical encoding.
Relevant for ICD, SNOMED, LOINC and FHIR mappings.

:param system   encoding system
:param code     system specific code
:param display  human readable description
"""
class Coding(BaseSchema):
    system: str | None = None

    code: str | None = None

    display: str | None = None