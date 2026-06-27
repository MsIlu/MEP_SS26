from __future__ import annotations

from careena4.core.engine import ExtractionEngine
from careena4.llm.call_control import CallModelConfig, TOPIC_LABELING_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.common import PipelineModel
from careena4.models.domain import MedicalCase
from careena4.server_log import log_event


class TopicLabelResult(PipelineModel):
    label: str


class TopicLabelBuilder:
    def __init__(
        self,
        *,
        extraction_engine: ExtractionEngine | None = None,
        call_model_config: CallModelConfig | None = None,
    ) -> None:
        self.extraction_engine = extraction_engine
        self.call_model_config = call_model_config

    def build(self, *, medical_case: MedicalCase) -> str | None:
        if medical_case.topic is None or not medical_case.topic.entries:
            return None
        llm_label = self._build_with_llm(medical_case=medical_case)
        if llm_label not in (None, ""):
            return llm_label
        return self._fallback_label(medical_case=medical_case)

    def _build_with_llm(self, *, medical_case: MedicalCase) -> str | None:
        if self.extraction_engine is None:
            return None
        prompt = load_prompt(TOPIC_LABELING_CALL)
        try:
            result = self.extraction_engine.extract(
                text=self._build_user_prompt(medical_case=medical_case),
                system_prompt=prompt.system_prompt,
                output_schema=TopicLabelResult,
                temperature=0.0,
                max_tokens=120,
                model=(
                    self.call_model_config.model_for(TOPIC_LABELING_CALL)
                    if self.call_model_config is not None
                    else None
                ),
                call_name=TOPIC_LABELING_CALL,
                prompt_name=prompt.name,
                prompt_version=prompt.version,
            )
        except Exception as exc:
            log_event(
                "topic.labeling.fallback_used",
                layer="application",
                reason=type(exc).__name__,
            )
            return None
        return result.label.strip()

    @staticmethod
    def _build_user_prompt(*, medical_case: MedicalCase) -> str:
        assert medical_case.topic is not None
        entry_lines = []
        for index, entry in enumerate(medical_case.topic.entries, start=1):
            source_span = entry.source.source_span or "none"
            entry_lines.append(
                f"{index}. topic_part={entry.topic_part}\n   source_span={source_span}"
            )
        return "Aktuelle Topic-Entries in Reihenfolge:\n" + "\n".join(entry_lines)

    @staticmethod
    def _fallback_label(*, medical_case: MedicalCase) -> str | None:
        if medical_case.topic is None or not medical_case.topic.entries:
            return None
        return medical_case.topic.entries[-1].topic_part.strip() or None
