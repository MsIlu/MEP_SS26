from openai import OpenAI
from extraction.core.exceptions import EmptyLLMResponseError
"""
Author @Freddy
    Thin transport layer for OpenAI-compatible LLM APIs.

    Responsible for:
    - sending chat completion requests
    - handling model selection
    - returning raw JSON-formatted responses

    Does NOT:
    - parse JSON
    - validate outputs
    - apply domain logic or prompts
"""
class LLMClient:

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
    ):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        self.default_model = model

    def complete(
        self,
        *,
        system_prompt: str,
        user_input: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        model: str | None = None,
    ) -> str:

        selected_model = model or self.default_model

        response = self.client.chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_input,
                },
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            
        )

        content = response.choices[0].message.content

        if not content:
            raise EmptyLLMResponseError("LLM returned empty response")

        return content