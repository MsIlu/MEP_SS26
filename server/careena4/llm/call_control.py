import os
from dataclasses import dataclass, field
from typing import Mapping


ENTRY_CALL = "entry_assessment"
EXTRACTION_CALL = "medical_extraction"
FOLLOWUP_CALL = "followup_resolution"
TURN_INTERPRETATION_CALL = "turn_interpretation"
QUESTION_RENDERING_CALL = "question_rendering"
RESPONSE_RENDERING_CALL = "response_rendering"
RECOMMENDATION_CALL = "recommendation_rendering"

CALL_MODEL_ENV_VARS = {
    ENTRY_CALL: "CAREENA4_ENTRY_MODEL",
    EXTRACTION_CALL: "CAREENA4_EXTRACTION_MODEL",
    FOLLOWUP_CALL: "CAREENA4_FOLLOWUP_MODEL",
    TURN_INTERPRETATION_CALL: "CAREENA4_TURN_INTERPRETER_MODEL",
    QUESTION_RENDERING_CALL: "CAREENA4_QUESTION_MODEL",
    RESPONSE_RENDERING_CALL: "CAREENA4_RESPONSE_MODEL",
    RECOMMENDATION_CALL: "CAREENA4_RECOMMENDATION_MODEL",
}


@dataclass(frozen=True)
class CallModelConfig:
    default_model: str
    overrides: Mapping[str, str] = field(default_factory=dict)

    def model_for(self, call_name: str) -> str:
        return self.overrides.get(call_name, self.default_model)


def build_call_model_config(
    *,
    default_model: str,
    overrides: Mapping[str, str] | None = None,
) -> CallModelConfig:
    merged_overrides = {
        call_name: model
        for call_name, model in {
            **_env_overrides(),
            **dict(overrides or {}),
        }.items()
        if model
    }
    return CallModelConfig(default_model=default_model, overrides=merged_overrides)


def _env_overrides() -> dict[str, str]:
    return {
        call_name: os.getenv(env_var, "").strip()
        for call_name, env_var in CALL_MODEL_ENV_VARS.items()
    }
