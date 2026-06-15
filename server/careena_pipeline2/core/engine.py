import json
import logging
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from careena_pipeline2.core.client import LLMClient
from careena_pipeline2.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)


T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


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
    ) -> T:
        logger.debug(
            "Starting extraction with schema=%s model=%s",
            output_schema.__name__,
            model or self.llm_client.default_model,
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
        )
        if not raw:
            raise EmptyLLMResponseError("LLM returned empty response")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse JSON response from LLM: %s", exc)
            logger.debug("Raw LLM response:\n%s", raw)
            raise InvalidJSONError(f"Failed to parse LLM JSON response: {exc}") from exc
        try:
            return output_schema.model_validate(parsed)
        except ValidationError as exc:
            logger.warning("Schema validation failed for %s: %s", output_schema.__name__, exc)
            logger.debug(
                "Invalid LLM JSON for %s:\n%s",
                output_schema.__name__,
                json.dumps(parsed, indent=2, ensure_ascii=False, default=str),
            )
            raise SchemaValidationError(
                f"{output_schema.__name__} validation failed: {exc}"
            ) from exc
