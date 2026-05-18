from pydantic import BaseModel, Field

"""
    Autor @Freddy
    First gate of the pipeline.

    Decides whether the input is medically relevant at all.
"""
class MedicalIntent(BaseModel):

    is_medical: bool = False

    confidence: float = Field(default=0.0, ge=0.0, le=1.0)