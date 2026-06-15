from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from careena_pipeline3.application.managers import DialogueManager, EntryManager, ExtractionManager
from careena_pipeline3.application.services import (
    IntentClassificationService,
)
from careena_pipeline3.core.client import LLMClient
from careena_pipeline3.core.engine import ExtractionEngine
from careena_pipeline3.infrastructure import CareenaPipeline3SessionStore
from careena_pipeline3.llm.call_control import CallModelConfig
from careena_pipeline3.llm import LLMCaseExtractionExtractor, LLMIntentGatewayExtractor
from careena_pipeline3.runtime import (
    LOCAL_LLM_MODEL,
    PipelineRuntimeServices,
    build_llm_client,
    build_pipeline_runtime,
)
from careena_pipeline3.simulation_runtime import SimulationRunner
from careena_pipeline3.simulation_runtime.adapters import CareenaPipeline3Adapter


@dataclass
class PipelineServices:
    llm_client: LLMClient
    extraction_engine: ExtractionEngine
    call_model_config: CallModelConfig
    intent_gateway_extractor: LLMIntentGatewayExtractor
    case_extraction_extractor: LLMCaseExtractionExtractor
    intent_classification_service: IntentClassificationService
    entry_manager: EntryManager
    extraction_manager: ExtractionManager
    dialogue_manager: DialogueManager
    session_store: CareenaPipeline3SessionStore


def build_default_services(
    *,
    llm_mode: Literal["env", "local"] = "env",
    call_models: dict[str, str] | None = None,
) -> PipelineServices:
    runtime = build_pipeline_runtime(
        llm_mode=llm_mode,
        call_models=call_models,
    )
    return PipelineServices(
        llm_client=runtime.llm_client,
        extraction_engine=runtime.extraction_engine,
        call_model_config=runtime.call_model_config,
        intent_gateway_extractor=runtime.intent_gateway_extractor,
        case_extraction_extractor=runtime.case_extraction_extractor,
        intent_classification_service=runtime.intent_classification_service,
        entry_manager=runtime.entry_manager,
        extraction_manager=runtime.extraction_manager,
        dialogue_manager=runtime.dialogue_manager,
        session_store=runtime.session_store,
    )


def build_simulation_runner(
    *,
    system_llm_mode: Literal["env", "local"] = "env",
    participant_llm_modes: tuple[str, ...] = ("env", "local"),
    call_models: dict[str, str] | None = None,
) -> SimulationRunner:
    runtime = build_pipeline_runtime(
        llm_mode=system_llm_mode,
        call_models=call_models,
    )
    participant_llms: dict[str, LLMClient] = {}
    for mode in participant_llm_modes:
        if mode == "env":
            participant_llms[mode] = build_llm_client(
                llm_mode="env",
                model_override=LOCAL_LLM_MODEL,
            )
            continue
        participant_llms[mode] = build_llm_client(llm_mode=mode)  # type: ignore[arg-type]
    return SimulationRunner(
        participant_llms=participant_llms,
        default_participant_llm_mode=participant_llm_modes[0],
        system_adapter=CareenaPipeline3Adapter(runtime.dialogue_manager),
    )
