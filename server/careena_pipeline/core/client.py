from openai import OpenAI

from careena_pipeline.core.exceptions import EmptyLLMResponseError


class LLMClient:
    """
    Lightweight client for OpenAI-compatible LLM APIs.

    This class acts only as a transport layer. It manages provider configuration,
    sends chat completion requests, and returns the raw text content.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        *,
        timeout: float = 60.0,
        max_retries: int = 1,
    ):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.default_model = model
        self.timeout = timeout
        self.max_retries = max_retries

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
