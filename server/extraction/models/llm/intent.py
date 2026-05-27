from pydantic import Field

from extraction.models.system.baseSchema import BaseSchema

"""
Author @Freddy
    First gate of the pipeline.

    Decides whether the input is medically relevant at all
    and if it contains relevant information to extract.
"""
class MedicalIntent(BaseSchema):

    is_medical: bool = False
    is_medical_confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    contains_extractable_information: bool = False