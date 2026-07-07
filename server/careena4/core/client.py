import os

from careena4.core.exceptions import EmptyLLMResponseError, LLMRequestError
from careena4.server_log import log_event, log_json

try:
    from openai import OpenAI
except ModuleNotFoundError:  # pragma: no cover - optional runtime dependency
    OpenAI = None  # type: ignore[assignment]

"""
Purpose: Wraps direct LLM access, checks model availability, and executes completion requests with logging and optional JSON mode.
Input: `messages`, model name, request parameters
Output: response text, availability status
Responsible: LLM requests, model healthcheck, request logging
Not responsible: schema validation, domain logic, prompt contents
"""
class LLMClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        *,
        timeout: float = 60.0,
        max_retries: int = 1,
    ):
        self.client = (
            OpenAI(
                base_url=base_url,
                api_key=api_key,
                timeout=timeout,
                max_retries=max_retries,
            )
            if OpenAI is not None
            else None
        )
        self.default_model = model

    def is_available(self) -> bool:
        return self.is_model_available(self.default_model)

    def is_model_available(self, model: str) -> bool:
        if self.client is None:
            return False
        try:
            self.client.with_options(
                timeout=15.0,
                max_retries=0,
            ).chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": "Antworte nur mit OK.",
                    },
                ],
                temperature=0.0,
                max_tokens=2,
            )
        except Exception as exc:
            log_event(
                "llm.health.failed",
                layer="core",
                model=model,
                reason=type(exc).__name__,
            )
            return False
        return True

    def complete(
        self,
        *,
        messages: list[dict],
        temperature: float = 0.0,
        max_tokens: int = 1000,
        model: str | None = None,
        json_mode: bool = False,
        call_name: str | None = None,
        prompt_name: str | None = None,
        prompt_version: str | None = None,
    ) -> str:
        selected_model = model or self.default_model
        prompt_chars = sum(len(str(message.get("content", ""))) for message in messages)
        log_event(
            "llm.complete.started",
            layer="core",
            call_name=call_name,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            model=selected_model,
            json_mode=json_mode,
            message_count=len(messages),
            prompt_chars=prompt_chars,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        if _prompt_debug_enabled():
            log_json(
                f"llm_prompt:{call_name or 'unknown'}",
                {
                    "call_name": call_name,
                    "prompt_name": prompt_name,
                    "prompt_version": prompt_version,
                    "model": selected_model,
                    "json_mode": json_mode,
                    "messages": messages,
                },
            )
        if self.client is None:
            if json_mode:
                raise LLMRequestError("OpenAI client dependency is not available")
            return "Ich weiss nicht genau."
        try:
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if json_mode else None,
            )
        except Exception as exc:
            log_event(
                "llm.complete.failed",
                layer="core",
                call_name=call_name,
                prompt_name=prompt_name,
                prompt_version=prompt_version,
                model=selected_model,
                reason=type(exc).__name__,
            )
            raise
        content = response.choices[0].message.content
        if not content:
            raise EmptyLLMResponseError("LLM returned empty response")
        log_event(
            "llm.complete.completed",
            layer="core",
            call_name=call_name,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            model=selected_model,
            output_chars=len(content),
        )
        return content


def _prompt_debug_enabled() -> bool:
    value = os.getenv("CAREENA4_LOG_PROMPTS", "").strip().casefold()
    return value in {"1", "true", "yes", "on"}
