from dataclasses import dataclass
from typing import Literal

import config

from careena_pipeline.core.client import LLMClient
from careena_pipeline.core.engine import ExtractionEngine
from careena_pipeline.pipeline import CareenaDecisionPipeline
from careena_pipeline.llm.call_control import build_call_model_config
from careena_pipeline.llm import (
    LLMCaseUpdateExtractor,
    LLMIntentGatewayExtractor,
    LLMNextStepAdvisor,
    LLMRoutingAdvisor,
)
from careena_pipeline.planning import RecommendationGate
from careena_pipeline.routing.fallback_engine import RecommendationEngine
from careena_pipeline.state import ConfirmationService, CareenaSessionStore
from careena_pipeline.tooling.scenario.runner import SyntheticPatientRunner


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
    intent_gateway_extractor: LLMIntentGatewayExtractor
    case_update_extractor: LLMCaseUpdateExtractor
    next_step_advisor: LLMNextStepAdvisor
    routing_advisor: LLMRoutingAdvisor
    decision_pipeline: CareenaDecisionPipeline
    session_store: CareenaSessionStore
    confirmation_service: ConfirmationService
    synthetic_patient_runner: SyntheticPatientRunner


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
    scenario_llm_mode: Literal["env", "local"] = "local",
) -> PipelineServices:
    llm_client = build_llm_client(llm_mode=llm_mode)
    scenario_llm_client = llm_client if scenario_llm_mode == llm_mode else build_llm_client(
        llm_mode=scenario_llm_mode
    )
    call_model_config = build_call_model_config(
        default_model=llm_client.default_model,
        overrides=call_models,
    )

    extraction_engine = ExtractionEngine(llm_client)
    intent_gateway_extractor = LLMIntentGatewayExtractor(
        extraction_engine,
        call_models=call_model_config,
    )
    case_update_extractor = LLMCaseUpdateExtractor(
        extraction_engine,
        call_models=call_model_config,
    )
    recommendation_gate = RecommendationGate()
    recommendation_engine = RecommendationEngine()
    next_step_advisor = LLMNextStepAdvisor(
        extraction_engine,
        recommendation_gate=recommendation_gate,
        call_models=call_model_config,
    )
    routing_advisor = LLMRoutingAdvisor(
        extraction_engine,
        fallback_engine=recommendation_engine,
        call_models=call_model_config,
    )
    decision_pipeline = CareenaDecisionPipeline(
        case_update_extractor,
        intent_gateway_extractor=intent_gateway_extractor,
        recommendation_gate=recommendation_gate,
        recommendation_engine=recommendation_engine,
        next_step_advisor=next_step_advisor,
        routing_advisor=routing_advisor,
    )
    session_store = CareenaSessionStore()
    confirmation_service = ConfirmationService()
    synthetic_patient_runner = SyntheticPatientRunner(
        patient_llms={
            llm_mode: llm_client,
            scenario_llm_mode: scenario_llm_client,
        },
        default_patient_llm_mode=scenario_llm_mode,
        decision_pipeline=decision_pipeline,
    )

    return PipelineServices(
        llm_client=llm_client,
        extraction_engine=extraction_engine,
        intent_gateway_extractor=intent_gateway_extractor,
        case_update_extractor=case_update_extractor,
        next_step_advisor=next_step_advisor,
        routing_advisor=routing_advisor,
        decision_pipeline=decision_pipeline,
        session_store=session_store,
        confirmation_service=confirmation_service,
        synthetic_patient_runner=synthetic_patient_runner,
    )
