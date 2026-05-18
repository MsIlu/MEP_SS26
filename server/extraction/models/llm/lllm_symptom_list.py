from pydantic import BaseModel

from extraction.models.llm.llm_symptom import LLMSymptom

"""
"""
class SymptomList(BaseModel):
    entities: list[LLMSymptom]