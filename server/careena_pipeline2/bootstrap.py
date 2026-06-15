from dataclasses import dataclass
import os
from typing import Literal

from careena_pipeline2.core.client import LLMClient
from careena_pipeline2.core.engine import ExtractionEngine
from careena_pipeline2.llm import MessageExtractor, build_call_model_config
from careena_pipeline2.pipeline import CareenaConversationPipeline
from careena_pipeline2.planning import DecisionPlanner
from careena_pipeline2.routing import RecommendationRouter
from careena_pipeline2.safety import SafetyGate
from careena_pipeline2.session import CareenaSessionStore
from careena_pipeline2.state import CaseUpdater, ConfirmationService
import config


LOCAL_LLM_BASE_URL = "http://localhost:11434/v1"
LOCAL_LLM_API_KEY = "ollama"
LOCAL_LLM_MODEL = "medgemma:4b"
ENV_LLM_BASE_URL = config.LITELLM_BASE_URL
ENV_LLM_API_KEY = config.LITELLM_API_KEY
ENV_LLM_MODEL = config.SELECTED_MODEL
DEFAULT_LLM_TIMEOUT_SECONDS = 60.0
DEFAULT_LLM_MAX_RETRIES = 1


@dataclass
class PipelineServices:
    llm_client: LLMClient
    extraction_engine: ExtractionEngine
    message_extractor: MessageExtractor
    decision_pipeline: CareenaConversationPipeline
    session_store: CareenaSessionStore
    confirmation_service: ConfirmationService


def build_llm_client(
    *,
    llm_mode: Literal["env", "local"] = "env",
) -> LLMClient:
    if llm_mode == "local":
        return LLMClient(
            base_url=LOCAL_LLM_BASE_URL,
            api_key=LOCAL_LLM_API_KEY,
            model=LOCAL_LLM_MODEL,
            timeout=DEFAULT_LLM_TIMEOUT_SECONDS,
            max_retries=DEFAULT_LLM_MAX_RETRIES,
        )
    return LLMClient(
        base_url=ENV_LLM_BASE_URL,
        api_key=ENV_LLM_API_KEY,
        model=ENV_LLM_MODEL,
        timeout=DEFAULT_LLM_TIMEOUT_SECONDS,
        max_retries=DEFAULT_LLM_MAX_RETRIES,
    )


def build_default_services(
    *,
    llm_mode: Literal["env", "local"] = "env",
    call_models: dict[str, str] | None = None,
) -> PipelineServices:
    llm_client = build_llm_client(llm_mode=llm_mode)
    extraction_engine = ExtractionEngine(llm_client)
    call_model_config = build_call_model_config(
        default_model=llm_client.default_model,
        overrides=call_models,
    )
    message_extractor = MessageExtractor(
        extraction_engine,
        call_models=call_model_config,
    )
    confirmation_service = ConfirmationService()
    decision_pipeline = CareenaConversationPipeline(
        message_extractor,
        safety_gate=SafetyGate(),
        case_updater=CaseUpdater(),
        confirmation_service=confirmation_service,
        planner=DecisionPlanner(),
        router=RecommendationRouter(),
    )
    session_store = CareenaSessionStore()
    return PipelineServices(
        llm_client=llm_client,
        extraction_engine=extraction_engine,
        message_extractor=message_extractor,
        decision_pipeline=decision_pipeline,
        session_store=session_store,
        confirmation_service=confirmation_service,
    )
