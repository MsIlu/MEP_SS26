from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import config

from careena_pipeline3.application.managers import (
    DialogueManager,
    EntryManager,
    ExtractionManager,
    ResponseManager,
)
from careena_pipeline3.application.services import (
    IntentClassificationService,
    RecommendationChoiceResolutionService,
    LLMResponseGenerationService,
    PythonExtractionResultNormalizer,
    ResponseGenerationService,
    ResilientExtractionService,
)
from careena_pipeline3.core.client import LLMClient
from careena_pipeline3.core.engine import ExtractionEngine
from careena_pipeline3.infrastructure import CareenaPipeline3SessionStore
from careena_pipeline3.server_log import configure_debug_logging
from careena_pipeline3.llm.call_control import CallModelConfig, build_call_model_config
from careena_pipeline3.llm import (
    LLMCaseExtractionExtractor,
    LLMIntentGatewayExtractor,
    LLMRecommendationChoiceExtractor,
)


LOCAL_LLM_BASE_URL = "http://localhost:11434/v1"
LOCAL_LLM_API_KEY = "ollama"
LOCAL_LLM_MODEL = "medgemma:27b"
ENV_LLM_BASE_URL = config.LITELLM_BASE_URL
ENV_LLM_API_KEY = config.LITELLM_API_KEY
ENV_LLM_MODEL = config.SELECTED_MODEL
DEFAULT_LLM_TIMEOUT_SECONDS = 60.0
DEFAULT_LLM_MAX_RETRIES = 1


@dataclass
class PipelineRuntimeServices:
    llm_client: LLMClient
    extraction_engine: ExtractionEngine
    call_model_config: CallModelConfig
    intent_gateway_extractor: LLMIntentGatewayExtractor
    case_extraction_extractor: LLMCaseExtractionExtractor
    recommendation_choice_extractor: LLMRecommendationChoiceExtractor
    extraction_result_normalizer: PythonExtractionResultNormalizer
    intent_classification_service: IntentClassificationService
    recommendation_choice_resolution_service: RecommendationChoiceResolutionService
    entry_manager: EntryManager
    extraction_manager: ExtractionManager
    dialogue_manager: DialogueManager
    session_store: CareenaPipeline3SessionStore


def build_llm_client(
    *,
    llm_mode: Literal["env", "local"] = "env",
    model_override: str | None = None,
) -> LLMClient:
    if llm_mode == "local":
        return LLMClient(
            base_url=LOCAL_LLM_BASE_URL,
            api_key=LOCAL_LLM_API_KEY,
            model=model_override or LOCAL_LLM_MODEL,
            timeout=DEFAULT_LLM_TIMEOUT_SECONDS,
            max_retries=DEFAULT_LLM_MAX_RETRIES,
        )

    return LLMClient(
        base_url=ENV_LLM_BASE_URL,
        api_key=ENV_LLM_API_KEY,
        model=model_override or ENV_LLM_MODEL,
        timeout=DEFAULT_LLM_TIMEOUT_SECONDS,
        max_retries=DEFAULT_LLM_MAX_RETRIES,
    )


def build_pipeline_runtime(
    *,
    llm_mode: Literal["env", "local"] = "env",
    call_models: dict[str, str] | None = None,
) -> PipelineRuntimeServices:
    configure_debug_logging()
    llm_client = build_llm_client(llm_mode=llm_mode)
    call_model_config = build_call_model_config(
        default_model=llm_client.default_model,
        overrides=call_models,
    )

    extraction_engine = ExtractionEngine(llm_client)
    intent_gateway_extractor = LLMIntentGatewayExtractor(
        extraction_engine,
        call_models=call_model_config,
    )
    case_extraction_extractor = LLMCaseExtractionExtractor(
        extraction_engine,
        call_models=call_model_config,
    )
    recommendation_choice_extractor = LLMRecommendationChoiceExtractor(
        extraction_engine,
        call_models=call_model_config,
    )
    extraction_result_normalizer = PythonExtractionResultNormalizer()
    intent_classification_service = IntentClassificationService(
        intent_gateway_extractor=intent_gateway_extractor,
    )
    recommendation_choice_resolution_service = RecommendationChoiceResolutionService(
        extractor=recommendation_choice_extractor,
    )
    entry_manager = EntryManager(
        intent_classification=intent_classification_service,
        recommendation_choice_resolution_service=recommendation_choice_resolution_service,
    )
    extraction_manager = ExtractionManager(
        extraction_service=ResilientExtractionService(
            case_extraction_extractor,
            result_normalizer=extraction_result_normalizer,
        ),
    )
    response_generation_service = ResponseGenerationService(
        llm_response_generation=LLMResponseGenerationService(llm_client=llm_client),
    )
    response_manager = ResponseManager(
        response_generation_service=response_generation_service,
    )
    dialogue_manager = DialogueManager(
        entry_manager=entry_manager,
        extraction_manager=extraction_manager,
        response_manager=response_manager,
    )
    session_store = CareenaPipeline3SessionStore()

    return PipelineRuntimeServices(
        llm_client=llm_client,
        extraction_engine=extraction_engine,
        call_model_config=call_model_config,
        intent_gateway_extractor=intent_gateway_extractor,
        case_extraction_extractor=case_extraction_extractor,
        recommendation_choice_extractor=recommendation_choice_extractor,
        extraction_result_normalizer=extraction_result_normalizer,
        intent_classification_service=intent_classification_service,
        recommendation_choice_resolution_service=recommendation_choice_resolution_service,
        entry_manager=entry_manager,
        extraction_manager=extraction_manager,
        dialogue_manager=dialogue_manager,
        session_store=session_store,
    )
