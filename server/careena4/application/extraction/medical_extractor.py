from __future__ import annotations

from careena4.core.engine import ExtractionEngine
from careena4.llm.call_control import CallModelConfig, EXTRACTION_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.turn import ExtractedCaseInput
from careena4.server_log import log_event


class MedicalExtractor:
    def __init__(
        self,
        *,
        extraction_engine: ExtractionEngine | None = None,
        call_model_config: CallModelConfig | None = None,
    ):
        self.extraction_engine = extraction_engine
        self.call_model_config = call_model_config

    def extract(
        self,
        *,
        message: str,
        history_messages: list[dict[str, str]] | None = None,
    ) -> ExtractedCaseInput:
        llm_result = self._extract_with_llm(
            message=message,
            history_messages=history_messages,
        )
        if llm_result is not None:
            return llm_result
        log_event(
            "extraction.medical.empty_result",
            layer="application",
            reason="llm_unavailable_or_failed",
        )
        return ExtractedCaseInput()

    def _extract_with_llm(
        self,
        *,
        message: str,
        history_messages: list[dict[str, str]] | None,
    ) -> ExtractedCaseInput | None:
        if self.extraction_engine is None:
            return None
        prompt = load_prompt(EXTRACTION_CALL)
        try:
            result = self.extraction_engine.extract(
                text=self._build_user_prompt(
                    message=message,
                    history_messages=history_messages,
                ),
                system_prompt=prompt.system_prompt,
                output_schema=ExtractedCaseInput,
                temperature=0.0,
                max_tokens=900,
                model=self.call_model_config.model_for(EXTRACTION_CALL) if self.call_model_config is not None else None,
                call_name=EXTRACTION_CALL,
                prompt_name=prompt.name,
                prompt_version=prompt.version,
            )
        except Exception as exc:
            log_event(
                "extraction.medical.llm_failed",
                layer="application",
                reason=type(exc).__name__,
            )
            return None

        log_event(
            "extraction.medical.completed",
            layer="application",
            observation_count=len(result.observations),
        )
        result.topic_label = None
        result.topic_description = None
        return result

    def _build_user_prompt(
        self,
        *,
        message: str,
        history_messages: list[dict[str, str]] | None,
    ) -> str:
        history_lines = []
        for item in history_messages or []:
            role = (item.get("role") or "unknown").strip()
            content = (item.get("content") or "").strip()
            if content:
                history_lines.append(f"- {role}: {content}")
        history_text = "\n".join(history_lines[-4:]) if history_lines else "- none"
        return (
            f"Letzte Konversation:\n{history_text}\n"
            f"Letzte Nutzernachricht:\n{message}"
        )
