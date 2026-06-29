from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Literal

from careena4.application import TurnEngine
from careena4.application.dialogue import QuestionBuilder, QuestionResolver, SafetyClarificationBuilder, SafetyClarificationResolver
from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.application.entry import EntryClassifier
from careena4.application.extraction import MedicalExtractor
from careena4.application.interpretation import TurnInterpreter
from careena4.application.safety import CaseSafetyEvaluator
from careena4.application.understanding import MedGemmaTurnUnderstandingService
from careena4.application.response import ResponseBuilder
from careena4.domain.case import CaseManager
from careena4.core.client import LLMClient
from careena4.core.engine import ExtractionEngine
from careena4.infrastructure import Careena4SessionStore, SafetyCatalogCache
from careena4.llm.call_control import CallModelConfig, build_call_model_config
from careena4.server_log import configure_debug_logging


try:  # pragma: no cover - runtime convenience
    import config as server_config
except ModuleNotFoundError:  # pragma: no cover - minimal test/runtime fallback
    server_config = None


LOCAL_LLM_BASE_URL = "http://localhost:11434/v1"
LOCAL_LLM_API_KEY = "ollama"
LOCAL_LLM_MODEL = "medgemma:27b"
ENV_LLM_BASE_URL = (
    server_config.LITELLM_BASE_URL
    if server_config is not None
    else os.getenv("LITELLM_BASE_URL", "http://localhost:4000").rstrip("/")
)
ENV_LLM_API_KEY = (
    server_config.LITELLM_API_KEY
    if server_config is not None
    else os.getenv("LITELLM_API_KEY", "")
)
ENV_LLM_MODEL = (
    server_config.SELECTED_MODEL
    if server_config is not None
    else os.getenv("LITELLM_MODEL", "medgemma:27b")
)
DEFAULT_LLM_TIMEOUT_SECONDS = 60.0
DEFAULT_LLM_MAX_RETRIES = 1


def _env_flag(name: str, *, default: bool = False) -> bool:
    """Read a boolean feature flag from the environment."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Careena4RuntimeServices:
    llm_client: LLMClient
    extraction_engine: ExtractionEngine
    call_model_config: CallModelConfig
    safety_catalog_cache: SafetyCatalogCache
    safety_clarification_builder: SafetyClarificationBuilder
    safety_clarification_resolver: SafetyClarificationResolver
    medical_extractor: MedicalExtractor
    question_resolver: QuestionResolver
    turn_engine: TurnEngine
    session_store: Careena4SessionStore


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


def build_runtime(
    *,
    llm_mode: Literal["env", "local"] = "env",
    call_models: dict[str, str] | None = None,
) -> Careena4RuntimeServices:
    configure_debug_logging()
    llm_client = build_llm_client(llm_mode=llm_mode)
    call_model_config = build_call_model_config(
        default_model=llm_client.default_model,
        overrides=call_models,
    )
    extraction_engine = ExtractionEngine(llm_client)
    safety_catalog_cache = SafetyCatalogCache()
    # Cache is NOT loaded here — main.py on_startup() loads it after catalog seeding.
    safety_clarification_builder = SafetyClarificationBuilder(
        llm_client=llm_client,
    )
    safety_clarification_resolver = SafetyClarificationResolver()
    case_manager = CaseManager()
    entry_classifier = EntryClassifier(
        extraction_engine=extraction_engine,
        call_model_config=call_model_config,
        case_manager=case_manager,
    )
    medical_extractor = MedicalExtractor(
        extraction_engine=extraction_engine,
        call_model_config=call_model_config,
    )
    turn_interpreter = TurnInterpreter(
        extraction_engine=extraction_engine,
        call_model_config=call_model_config,
    )
    question_resolver = QuestionResolver(
        safety_clarification_resolver=safety_clarification_resolver,
        extraction_engine=extraction_engine,
        call_model_config=call_model_config,
    )
    question_builder = QuestionBuilder(
        llm_client=llm_client,
        call_model_config=call_model_config,
    )
    response_builder = ResponseBuilder(
        llm_client=llm_client,
        call_model_config=call_model_config,
        case_manager=case_manager,
    )
    turn_understanding_service = MedGemmaTurnUnderstandingService(
        extraction_engine=extraction_engine,
    )
    raw_red_flag_detector = RawRedFlagDetector(catalog_cache=safety_catalog_cache)
    case_safety_evaluator = CaseSafetyEvaluator(
        catalog_cache=safety_catalog_cache,
        llm_client=llm_client,
    )
    turn_engine = TurnEngine(
        raw_red_flag_detector=raw_red_flag_detector,
        case_safety_evaluator=case_safety_evaluator,
        safety_clarification_builder=safety_clarification_builder,
        entry_classifier=entry_classifier,
        question_resolver=question_resolver,
        medical_extractor=medical_extractor,
        case_manager=case_manager,
        question_builder=question_builder,
        response_builder=response_builder,
        turn_interpreter=turn_interpreter,
        turn_understanding_service=turn_understanding_service,
    )
    session_store = Careena4SessionStore()
    return Careena4RuntimeServices(
        llm_client=llm_client,
        extraction_engine=extraction_engine,
        call_model_config=call_model_config,
        safety_catalog_cache=safety_catalog_cache,
        safety_clarification_builder=safety_clarification_builder,
        safety_clarification_resolver=safety_clarification_resolver,
        medical_extractor=medical_extractor,
        question_resolver=question_resolver,
        turn_engine=turn_engine,
        session_store=session_store,
    )
