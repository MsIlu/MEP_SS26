import json
import logging
from time import perf_counter
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from careena4.core.client import LLMClient
from careena4.core.exceptions import EmptyLLMResponseError, InvalidJSONError, SchemaValidationError
from careena4.server_log import log_event, log_json


T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

"""
Purpose: Generic extraction engine that runs structured LLM extraction, parses JSON responses, and validates them against any provided Pydantic schema.
Input: `text`, `system_prompt`, `output_schema`
Output: validated schema object, core errors
Responsible: JSON parsing, schema validation, extraction logging
Not responsible: API transport, domain decisions, persistence
"""
class ExtractionEngine:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def extract(
        self,
        *,
        text: str,
        system_prompt: str,
        output_schema: Type[T],
        temperature: float = 0.0,
        max_tokens: int = 1000,
        model: str | None = None,
        call_name: str | None = None,
        prompt_name: str | None = None,
        prompt_version: str | None = None,
    ) -> T:
        started_at = perf_counter()
        selected_model = model or self.llm_client.default_model
        log_event(
            "llm.extract.started",
            layer="core",
            call_name=call_name,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            schema=output_schema.__name__,
            model=selected_model,
            prompt_chars=len(system_prompt),
            input_chars=len(text),
            max_tokens=max_tokens,
            temperature=temperature,
        )
        raw = self.llm_client.complete(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            json_mode=True,
            call_name=call_name,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
        )
        if not raw:
            raise EmptyLLMResponseError("LLM returned empty response")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            log_event(
                "llm.extract.invalid_json",
                layer="core",
                call_name=call_name,
                prompt_name=prompt_name,
                prompt_version=prompt_version,
                schema=output_schema.__name__,
                model=selected_model,
                duration_ms=round((perf_counter() - started_at) * 1000, 2),
                error=str(exc),
                level=logging.WARNING,
            )
            raise InvalidJSONError(f"Failed to parse LLM JSON response: {exc}") from exc
        try:
            validated = output_schema.model_validate(parsed)
        except ValidationError as exc:
            log_event(
                "llm.extract.schema_validation_failed",
                layer="core",
                call_name=call_name,
                prompt_name=prompt_name,
                prompt_version=prompt_version,
                schema=output_schema.__name__,
                model=selected_model,
                duration_ms=round((perf_counter() - started_at) * 1000, 2),
                error=str(exc),
                level=logging.WARNING,
            )
            raise SchemaValidationError(f"{output_schema.__name__} validation failed: {exc}") from exc
        log_json(_validated_json_log_title(call_name=call_name, output_schema=output_schema), parsed)
        log_event(
            "llm.extract.completed",
            layer="core",
            call_name=call_name,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            schema=output_schema.__name__,
            model=selected_model,
            duration_ms=round((perf_counter() - started_at) * 1000, 2),
        )
        logger.debug("Validated schema=%s", output_schema.__name__)
        return validated


def _validated_json_log_title(*, call_name: str | None, output_schema: Type[T]) -> str:
    if call_name:
        return f"llm_validated_json:{call_name}:{output_schema.__name__}"
    return f"llm_validated_json:{output_schema.__name__}"
