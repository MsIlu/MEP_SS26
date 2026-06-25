from openai import OpenAI
from extraction.core.exceptions import EmptyLLMResponseError
"""
Author @Freddy
    Lightweight client for OpenAI-compatible LLM APIs.

    LLMClient is responsible for sending chat completion requests
    to a configured language model provider and returning the raw response.

    Responsibilities:
    - initialize and manage the OpenAI-compatible client
    - send chat completion requests
    - handle model selection
    - provide configurable generation parameters
    - return raw model output as text

    The client acts purely as a transport layer between the application
    and the language model provider.

    Supported providers may include:
    - OpenAI
    - Ollama
    - LiteLLM
    - other OpenAI-compatible APIs

    Request flow:
    1. build chat completion request
    2. send request to the configured provider
    3. receive model response
    4. return raw response content

    The client does NOT:
    - parse JSON responses
    - validate schemas
    - contain extraction logic
    - apply domain-specific reasoning
    - implement pipeline orchestration

    Error handling:
    If the model returns an empty response,
    an EmptyLLMResponseError is raised.

    Notes:
    The client allows normal text output or enforced JSON output
    by toggling json_mode on/off.
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
        messages: list[dict],
        temperature: float = 0.0,
        max_tokens: int = 1000,
        model: str | None = None,
        json_mode: bool = False,
    ) -> str:

        selected_model = model or self.default_model

        response = self.client.chat.completions.create(
            model=selected_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"} if json_mode else None,
            
        )

        content = response.choices[0].message.content

        if not content:
            raise EmptyLLMResponseError("LLM returned empty response")

        return content