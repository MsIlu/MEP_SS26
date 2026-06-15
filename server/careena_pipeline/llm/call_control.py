import os
from dataclasses import dataclass, field
from typing import Mapping


INTENT_GATEWAY_CALL = "intent_gateway"
CASE_UPDATE_CALL = "case_update"
NEXT_STEP_CALL = "next_step"
ROUTING_CALL = "routing"

PRIMARY_CALL_SEQUENCE = (
    INTENT_GATEWAY_CALL,
    CASE_UPDATE_CALL,
    ROUTING_CALL,
)

CALL_STAGE_LABELS = {
    INTENT_GATEWAY_CALL: "call_1",
    CASE_UPDATE_CALL: "call_2",
    ROUTING_CALL: "call_3",
    NEXT_STEP_CALL: "support_call",
}

CALL_MODEL_ENV_VARS = {
    INTENT_GATEWAY_CALL: "CAREENA_INTENT_GATEWAY_MODEL",
    CASE_UPDATE_CALL: "CAREENA_CASE_UPDATE_MODEL",
    NEXT_STEP_CALL: "CAREENA_NEXT_STEP_MODEL",
    ROUTING_CALL: "CAREENA_ROUTING_MODEL",
}


@dataclass(frozen=True)
class CallModelConfig:
    """
    Resolves which concrete model should be used for each LLM call.

    The goal is to keep the primary call structure explicit:
    - Call 1: intent gateway
    - Call 2: case update extraction
    - Call 3: routing / recommendation
    - support_call: optional next-step wording helper
    """

    default_model: str
    overrides: Mapping[str, str] = field(default_factory=dict)

    def model_for(self, call_name: str) -> str:
        return self.overrides.get(call_name, self.default_model)

    def stage_for(self, call_name: str) -> str:
        return CALL_STAGE_LABELS.get(call_name, "unknown_call")


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
    return CallModelConfig(
        default_model=default_model,
        overrides=merged_overrides,
    )


def _env_overrides() -> dict[str, str]:
    return {
        call_name: os.getenv(env_var, "").strip()
        for call_name, env_var in CALL_MODEL_ENV_VARS.items()
    }
