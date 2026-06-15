from typing import Any, Literal

from pydantic import Field

from careena_pipeline.models.common.base import PipelineModel


class SimulationRequest(PipelineModel):
    scenario_prompt: str = Field(
        ...,
        description="Freitext-Szenario fuer die simulierte Person.",
    )
    participant_prompt: str = Field(
        default="",
        description="Systemprompt fuer Verhalten und Sprachstil der simulierten Person.",
    )
    opening_message: str | None = Field(
        default=None,
        description="Optionale erste Nachricht der simulierten Person.",
    )
    max_turns: int = Field(default=6, ge=1, le=20)
    participant_llm_mode: Literal["env", "local"] | None = Field(
        default=None,
        description="Optionaler LLM-Modus fuer die simulierte Person.",
    )
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
