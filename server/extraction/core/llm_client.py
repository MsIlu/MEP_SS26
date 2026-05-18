from openai import OpenAI
"""
Author @Freddy

LLMClient provides a wrapper arount the OpenAI API-
It is initialized with base_url, api_key and model to configure
the LLM connection.
the complete() method accepts a system_prompt, user_input and optional generation settings.
It sends a request to the configured model and returns the generated response
as JSON formatted string.

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

        self.model = model

    def complete(
        self,
        *,
        system_prompt: str,
        user_input: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
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
            raise ValueError("Empty LLM response")

        return content