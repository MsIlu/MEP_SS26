from __future__ import annotations

from careena_pipeline3.models.extraction import Call2ExtractionResult


class ExtractionFailureFallbackBuilder:
    """Builds a small contract-stable fallback when the primary Call 2 fails."""

    def build(
        self,
        *,
        pending_slot: str | None = None,
    ) -> Call2ExtractionResult:
        return Call2ExtractionResult(
            open_questions=[pending_slot] if pending_slot else [],
            extraction_notes=["case_extraction_failed"],
            trace_notes=["case_extraction_failed"],
        )
