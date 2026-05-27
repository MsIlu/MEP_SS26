from extraction.core.extraction_engine import ExtractionEngine
from extraction.models.llm.observation_event_list import ObservationEventList
from extraction.prompts.event_prompt import EVENT_SYSTEM_PROMPT

"""
Author @Freddy
    Extracts structured medical observations from text.

    Each observation represents:
    - symptoms
    - diagnoses
    - medications
    - medical findings

    Responsible for:
    - converting unstructured text into ObservationEvent objects
    - preserving exact source spans
    - capturing minimal contextual metadata (negation, certainty, temporality)
"""
class EventExtractor:

    def __init__(self, engine: ExtractionEngine):
        self.engine = engine

    def extract(self, text: str) -> ObservationEventList:
        return self.engine.extract(
            text=text,
            system_prompt=EVENT_SYSTEM_PROMPT,
            output_schema=ObservationEventList,
        )