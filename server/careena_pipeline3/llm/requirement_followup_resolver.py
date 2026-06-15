import json

from careena_pipeline3.core.engine import ExtractionEngine
from careena_pipeline3.llm.call_control import (
    CallModelConfig,
    REQUIREMENT_FOLLOWUP_CALL,
)
from careena_pipeline3.llm.prompts.requirement_followup import (
    REQUIREMENT_FOLLOWUP_SYSTEM_PROMPT,
)
from careena_pipeline3.models.domain import PendingFollowup
from careena_pipeline3.models.turn import RequirementFollowupResolutionResult
from careena_pipeline3.server_log.logging import log_json


class LLMRequirementFollowupResolver:
    def __init__(
        self,
        engine: ExtractionEngine,
        call_models: CallModelConfig | None = None,
    ):
        self.engine = engine
        self.call_models = call_models

    def resolve(
        self,
        *,
        latest_user_message: str,
        pending_followup: PendingFollowup,
        last_assistant_question: str | None = None,
        current_value: str | int | None = None,
        allowed_answer_shape: str | None = None,
    ) -> RequirementFollowupResolutionResult:
        payload = {
            "latest_user_message": latest_user_message,
            "requirement_key": pending_followup.requirement_key,
            "slot": pending_followup.slot,
            "focus_observation_id": pending_followup.focus_observation_id,
            "focus_label": pending_followup.focus_label,
            "last_assistant_question": last_assistant_question,
            "current_value": current_value,
            "allowed_answer_shape": allowed_answer_shape,
        }
        log_json("REQUIREMENT FOLLOWUP RESOLUTION CONTEXT", payload)
        result = self.engine.extract(
            text=json.dumps(payload, ensure_ascii=False),
            system_prompt=REQUIREMENT_FOLLOWUP_SYSTEM_PROMPT,
            output_schema=RequirementFollowupResolutionResult,
            max_tokens=250,
            model=(
                self.call_models.model_for(REQUIREMENT_FOLLOWUP_CALL)
                if self.call_models is not None
                else None
            ),
        )
        log_json("REQUIREMENT FOLLOWUP RESOLUTION RESULT", result)
        return result
