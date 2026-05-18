from extraction.core.extraction_engine import ExtractionEngine
from extraction.prompts.intent_prompt import INTENT_SYSTEM_PROMPT
from extraction.models.llm.llm_intent import MedicalIntent

"""
    Author @Freddy
    Wrapper based on extraction engine.
    Decides whether input is medically relevant.
"""
class MedicalIntentExtractor:


    def __init__(self, engine: ExtractionEngine):
        self.engine = engine

    def extract(self, text: str) -> MedicalIntent:

        return self.engine.extract(
            text=text,
            system_prompt=INTENT_SYSTEM_PROMPT,
            output_schema=MedicalIntent,
        )