import config

from extraction.pipeline.extractor_intent import MedicalIntentExtractor
from extraction.core.extraction_engine import ExtractionEngine
from extraction.models.llm.pipeline_result import PipelineResult
from extraction.pipeline.extractor_events import EventExtractor

"""
Author @Freddy
    High-level orchestration layer for the extraction workflow.

    The ExtractionPipeline coordinates the execution order of
    multiple extraction components and combines their outputs
    into a single structured pipeline result.

    Current pipeline flow:
    1. classify whether the input is medically relevant
    2. stop processing for non-medical inputs
    3. extract structured medical observations

    Responsibilities:
    - coordinate extraction steps
    - manage pipeline execution flow
    - apply early stopping for irrelevant inputs
    - combine extraction results into a unified response object

    The pipeline itself does not contain extraction logic.
    Individual extraction tasks are delegated to specialized extractors.

    Current components:
    - MedicalIntentExtractor
    - EventExtractor

    Design goals:
    - modular pipeline structure
    - easy extension with additional extractors
    - clear separation between orchestration and extraction logic
    - reusable extraction workflow composition

    The pipeline does NOT:
    - communicate with LLM providers directly
    - define prompts or schemas
    - validate raw model outputs
    - implement medical reasoning

    Notes:
    The current extraction flow is intentionally lightweight
    and expected to evolve iteratively as the medical data model,
    relation handling, and extraction semantics evolve.
"""
class ExtractionPipeline:

    # Specific extractors are initialized here
    def __init__(self, engine: ExtractionEngine):

        self.intent = MedicalIntentExtractor(engine)
        self.events = EventExtractor(engine)

    # Defines execution order and logic of extraction steps
    def run(self, text: str) -> PipelineResult:

        # 1. Intent Gate
        intent = self.intent.extract(text)

        if not intent.is_medical:
            return PipelineResult(
                intent=intent,
                observations=None
            )

        # 2. Symptom extraction (not final)

        observations = self.events.extract(text)

        return PipelineResult(
            intent=intent,
            observations=observations,
        )