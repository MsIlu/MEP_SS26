"""Public composition root for the Careena4 runtime.

main.py calls build_default_services() once at import time; the returned
Careena4Services bundle exposes only what the web layer needs. The full wiring
lives in runtime.build_runtime().
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from careena4.application import TurnEngine
from careena4.core.client import LLMClient
from careena4.core.engine import ExtractionEngine
from careena4.infrastructure import Careena4SessionStore, SafetyCatalogCache
from careena4.llm.call_control import CallModelConfig
from careena4.runtime import LOCAL_LLM_MODEL, build_llm_client, build_runtime
from careena4.simulation_runtime import SimulationRunner
from careena4.simulation_runtime.adapters.careena4 import Careena4Adapter


@dataclass
class Careena4Services:
    """Slim service bundle handed to the web layer (subset of the runtime graph)."""

    llm_client: LLMClient
    extraction_engine: ExtractionEngine
    call_model_config: CallModelConfig
    turn_engine: TurnEngine
    session_store: Careena4SessionStore
    safety_catalog_cache: SafetyCatalogCache


def build_default_services(
    *,
    llm_mode: Literal["env", "local"] = "env",
    call_models: dict[str, str] | None = None,
) -> Careena4Services:
    """Build the production service graph.

    llm_mode "env" reads the LiteLLM endpoint from config/.env; "local" targets
    a local Ollama instance directly.
    """
    runtime = build_runtime(llm_mode=llm_mode, call_models=call_models)
    return Careena4Services(
        llm_client=runtime.llm_client,
        extraction_engine=runtime.extraction_engine,
        call_model_config=runtime.call_model_config,
        turn_engine=runtime.turn_engine,
        session_store=runtime.session_store,
        safety_catalog_cache=runtime.safety_catalog_cache,
    )


def build_simulation_runner(
    *,
    system_llm_mode: Literal["env", "local"] = "env",
    participant_llm_modes: tuple[str, ...] = ("env", "local"),
    call_models: dict[str, str] | None = None,
) -> SimulationRunner:
    """Build the runner behind /simulation/run and the /simrun chat command.

    The "system" side is a full Careena4 runtime; each participant mode gets
    its own LLM client to play the simulated user.
    """
    runtime = build_runtime(llm_mode=system_llm_mode, call_models=call_models)
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
        system_adapter=Careena4Adapter(runtime.turn_engine),
    )
