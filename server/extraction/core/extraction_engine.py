import json
from typing import TypeVar, Type
from pydantic import BaseModel

from extraction.core.llm_client import LLMClient

T = TypeVar("T", bound=BaseModel)

"""
Author @ Freddy

Extraction Engine is a reusable component.
It takes in text, system_prompt and output_schema based on a pydantic model
The engine sends a request to the LLMClient,
parses the JSON response and validated it against the provided schema.
Exceptions are raised if the response is empty, invalid or does not match schema 
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
    ) -> T:

        raw = self.llm_client.complete(
            system_prompt=system_prompt,
            user_input=text,
        )
        if not raw:
            raise ValueError("Empty LLM response")
        
        parsed = json.loads(raw)

        #DEV DEBUG
        print(json.dumps(parsed, indent=2, ensure_ascii=False))

        validated = output_schema.model_validate(parsed)

        return validated