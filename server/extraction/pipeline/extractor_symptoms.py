from pydantic import BaseModel

from extraction.core.extraction_engine import ExtractionEngine
from extraction.prompts.symptom_prompt import SYMPTOM_SYSTEM_PROMPT
from extraction.models.llm.lllm_symptom_list import SymptomList
from extraction.models.llm.llm_symptom import LLMSymptom

"""
    Author @Freddy
    Wrapper based on extraction engine.
"""
class SymptomExtractor:

    def __init__(self, engine: ExtractionEngine):
        self.engine = engine

    def extract(self, text: str) -> SymptomList:

        return self.engine.extract(
            text=text,
            system_prompt=SYMPTOM_SYSTEM_PROMPT,
            output_schema=SymptomList,
        )