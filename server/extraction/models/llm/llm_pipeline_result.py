from pydantic import BaseModel

from extraction.models.llm.llm_intent import MedicalIntent
from extraction.models.llm.llm_scope import ExtractionScope
from extraction.pipeline.symptom_extractor import SymptomList

"""
    Autor @Freddy    
"""
class PipelineResult(BaseModel):

    intent: MedicalIntent

    scope: ExtractionScope | None = None

    symptoms: SymptomList | None = None