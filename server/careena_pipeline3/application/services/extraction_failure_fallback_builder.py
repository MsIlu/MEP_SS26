from __future__ import annotations

from careena_pipeline3.models.extraction import ExtractionResult


class ExtractionFailureFallbackBuilder:
    """Builds a small contract-stable fallback when the primary Call 2 fails."""

    def build(
        self,
        *,
        raw_text: str,
        pending_slot: str | None = None,
    ) -> ExtractionResult:
        return ExtractionResult(
            raw_text=raw_text,
            case_payload={
                "unresolved_questions": [pending_slot] if pending_slot else [],
                "extraction_notes": ["case_extraction_failed"],
            },
            trace_notes=["case_extraction_failed"],
        )
