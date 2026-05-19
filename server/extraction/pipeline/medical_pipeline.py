import config

from extraction.pipeline.extractor_intent import MedicalIntentExtractor
from extraction.pipeline.extractor_scope import ScopeExtractor
from extraction.pipeline.extractor_symptoms import SymptomExtractor
from extraction.core.llm_client import LLMClient
from extraction.core.extraction_engine import ExtractionEngine
from extraction.models.llm.llm_pipeline_result import PipelineResult

class MedicalPipeline:
    """
    Author @Freddy
    Orchestrates full medical extraction flow:
    Intent → Scope → Extraction → Graph
    """

    def __init__(self):

        llm_client = LLMClient(
            base_url=config.LITELLM_BASE_URL,
            api_key=config.LITELLM_API_KEY,
            model="medgemma:4b",
        )

        engine = ExtractionEngine(llm_client)

        self.intent = MedicalIntentExtractor(engine)
        self.scope = ScopeExtractor(engine)
        self.symptom_extractor = SymptomExtractor(engine)

    def run(self, text: str) -> PipelineResult:

        # 1. Intent Gate
        intent = self.intent.extract(text)

        if not intent.is_medical:
            return PipelineResult(
                intent=intent,
                scope=None,
                symptoms=None
            )

        # 2. Scope Routing
        scope = self.scope.extract(text)

        should_extract = (
            scope.has_symptoms
            or scope.has_medications
            or scope.has_conditions
            or scope.has_events
            or scope.has_concerns
        )

        if not should_extract:
            return PipelineResult(
                intent=intent,
                scope=scope,
                symptoms=None,
            )

        # 3. Symptom extraction (not final)
        symptoms = None

        if scope.has_symptoms:
            symptoms = self.symptom_extractor.extract(text)

        return PipelineResult(
            intent=intent,
            scope=scope,
            symptoms=symptoms,
        )
