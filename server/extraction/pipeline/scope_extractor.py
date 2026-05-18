from extraction.core.extraction_engine import ExtractionEngine
from extraction.prompts.scope_prompt import SCOPE_SYSTEM_PROMPT
from extraction.models.llm.llm_scope import ExtractionScope


class ScopeExtractor:
    """
    Author @Freddy
    Determines which extraction pipelines should run.
    """

    def __init__(self, engine: ExtractionEngine):
        self.engine = engine

    def extract(self, text: str) -> ExtractionScope:

        return self.engine.extract(
            text=text,
            system_prompt=SCOPE_SYSTEM_PROMPT,
            output_schema=ExtractionScope,
        )