from typing import Literal

from pydantic import Field

from careena_pipeline.models.common.base import PipelineModel


class SafetyResult(PipelineModel):
    red_flag_detected: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    matched_flags: list[str] = Field(default_factory=list)
    checked_sources: list[str] = Field(default_factory=list)
    action: Literal["continue", "interrupt_emergency_flow"] = "continue"
    severity: str | None = None
    rule_id: str | None = None
    rule_name: str | None = None
    category: str | None = None
    message_key: str | None = None
    matched_keywords: list[str] = Field(default_factory=list)
