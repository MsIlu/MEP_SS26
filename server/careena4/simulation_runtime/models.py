from typing import Any, Literal

from pydantic import Field

from careena4.models.common import PipelineModel


class SimulationRequest(PipelineModel):
    scenario_prompt: str
    participant_prompt: str = ""
    opening_message: str | None = None
    max_turns: int = Field(default=12, ge=1, le=20)
    participant_llm_mode: Literal["env", "local"] | None = None
    participant_model: str | None = None
    participant_temperature: float = Field(default=0.25, ge=0.0, le=1.5)


class SimulationTranscriptEntry(PipelineModel):
    role: str
    content: str
    response_mode: str | None = None


class SimulationSystemTurn(PipelineModel):
    text: str
    response_mode: str | None = None
    should_stop: bool = False
    stop_reason: str | None = None
    summary: dict[str, Any] | None = None
    state: Any = None
    raw_result: Any = None


class SimulationResult(PipelineModel):
    transcript: list[SimulationTranscriptEntry] = Field(default_factory=list)
    final_summary: dict[str, Any] | None = None
    final_system_state: Any = None
    final_system_result: Any = None
    stopped_reason: str
