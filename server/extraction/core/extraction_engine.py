import json
from typing import TypeVar, Type
from pydantic import BaseModel, ValidationError
import logging

from extraction.core.llm_client import LLMClient
from extraction.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
"""
Author @Freddy
    Generic structured extraction engine.

    The ExtractionEngine is the core component responsible for running
    schema-based LLM extractions.

    Responsibilities:
    - execute LLM requests via LLMClient
    - enforce structured JSON outputs
    - parse raw LLM responses
    - validate responses against Pydantic schemas
    - return validated and typed objects
    - provide centralized logging and extraction error handling

    The engine is fully domain-independent.
    It can be used for medical extraction, but also for any other
    structured extraction task.

    Extraction flow:
    1. send system prompt and user input to the LLM
    2. receive raw model output
    3. parse the output as JSON
    4. validate the parsed data against the provided schema
    5. return the validated schema object

    Validation:
    The output of every extraction step is validated using Pydantic.
    This ensures that downstream components only receive structured,
    well-defined data.

    Error handling:
    Common extraction failures are converted into dedicated exceptions:
    - EmptyLLMResponseError
    - InvalidJSONError
    - SchemaValidationError

    Typing:
    The generic type parameter `T` ensures that the returned object
    matches the provided output schema.

    Example:
        result = engine.extract(
            text="YOUR_INPUT_TEXT",
            system_prompt=YOUR_PROMPT,
            output_schema=YOUR_PYDANTIC_SCHEMA,
        )

        # result is typed your provided pydantic type

    The engine does NOT:
    - contain domain-specific logic
    - define prompts
    - implement extraction strategies
    - perform medical reasoning
    - communicate with providers directly
"""

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

        messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ]

        raw = self.llm_client.complete(
            messages = messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            json_mode=True,
        )

        if not raw:
            logger.error(
                "LLM returned empty response"
                ) 

            raise EmptyLLMResponseError("LLM returned empty response")
        

        try:
            parsed = json.loads(raw)

        except json.JSONDecodeError as e:
            logger.exception(
                "Failed to parse JSON response from LLM"
                )

            raise InvalidJSONError(
                f"Failed to parse LLM JSON response: {e}"
            ) from e

        logger.debug(
            "Parsed extraction output:\n%s",
            json.dumps(parsed, indent=2, ensure_ascii=False)
        )

        try:
            validated = output_schema.model_validate(parsed)

        except ValidationError as e:
            logger.exception(
                "Schema validation failed for %s",
                output_schema.__name__,
                )
            
            raise SchemaValidationError(
                f"{output_schema.__name__} validation failed: {e}"
            ) from e

        logger.debug(
            "Successfully validated schema=%s",
            output_schema.__name__,
            )
        
        return validated