from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from careena_pipeline.pipeline import CareenaDecisionPipeline
from careena_pipeline.runtime import (
    PipelineRuntimeServices,
    build_llm_client,
    build_pipeline_runtime,
)

if TYPE_CHECKING:
    from careena_pipeline.core.client import LLMClient
    from careena_pipeline.core.engine import ExtractionEngine
    from careena_pipeline.llm import (
        LLMCaseUpdateExtractor,
        LLMIntentGatewayExtractor,
        LLMNextStepAdvisor,
        LLMRoutingAdvisor,
    )
    from careena_pipeline.simulation_runtime.runner import SimulationRunner
    from careena_pipeline.state import ConfirmationService, CareenaSessionStore


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
    simulation_runner: SimulationRunner


@dataclass
class ToolingServices:
    simulation_runner: SimulationRunner


def build_default_services(
    *,
    llm_mode: Literal["env", "local"] = "env",
    call_models: dict[str, str] | None = None,
    scenario_llm_mode: Literal["env", "local"] = "local",
) -> PipelineServices:
    runtime = build_pipeline_runtime(
        llm_mode=llm_mode,
        call_models=call_models,
    )
    tooling = build_tooling_services(
        decision_pipeline=runtime.decision_pipeline,
        primary_llm_client=runtime.llm_client,
        primary_llm_mode=llm_mode,
        scenario_llm_mode=scenario_llm_mode,
    )

    return PipelineServices(
        llm_client=runtime.llm_client,
        extraction_engine=runtime.extraction_engine,
        intent_gateway_extractor=runtime.intent_gateway_extractor,
        case_update_extractor=runtime.case_update_extractor,
        next_step_advisor=runtime.next_step_advisor,
        routing_advisor=runtime.routing_advisor,
        decision_pipeline=runtime.decision_pipeline,
        session_store=runtime.session_store,
        confirmation_service=runtime.confirmation_service,
        simulation_runner=tooling.simulation_runner,
    )


def build_tooling_services(
    *,
    decision_pipeline: CareenaDecisionPipeline,
    primary_llm_client: LLMClient,
    primary_llm_mode: Literal["env", "local"],
    scenario_llm_mode: Literal["env", "local"] = "local",
) -> ToolingServices:
    from careena_pipeline.simulation_runtime.adapters import CareenaPipelineAdapter
    from careena_pipeline.simulation_runtime.runner import SimulationRunner

    scenario_llm_client = (
        primary_llm_client
        if scenario_llm_mode == primary_llm_mode
        else build_llm_client(llm_mode=scenario_llm_mode)
    )
    simulation_runner = SimulationRunner(
        participant_llms={
            primary_llm_mode: primary_llm_client,
            scenario_llm_mode: scenario_llm_client,
        },
        default_participant_llm_mode=scenario_llm_mode,
        system_adapter=CareenaPipelineAdapter(decision_pipeline),
    )
    return ToolingServices(
        simulation_runner=simulation_runner,
    )
