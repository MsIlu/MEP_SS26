from extraction.core.extraction_engine import ExtractionEngine
from extraction.prompts.intent_prompt import INTENT_SYSTEM_PROMPT
from extraction.models.llm.intent import MedicalIntent

"""
Author @Freddy
    Extracts whether input is medically relevant
    and whether it contains extractable medical information.

    Acts as the first gate of the pipeline.
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