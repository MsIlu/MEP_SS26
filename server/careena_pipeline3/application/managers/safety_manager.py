from careena_pipeline3.application.services.raw_red_flag_detector import (
    RawRedFlagDetector,
)
from careena_pipeline3.models.domain import MedicalCase
from careena_pipeline3.models.turn import ExtractionPayload, SafetyState, TurnInput


class SafetyManager:
    """Runs turn-level safety checks for raw and normalized inputs."""

    def __init__(
        self,
        raw_red_flag_detector: RawRedFlagDetector | None = None,
    ) -> None:
        # Allow dependency injection for tests and future detector variants.
        self._raw_red_flag_detector = raw_red_flag_detector or RawRedFlagDetector()

    def assess_raw_message(self, turn_input: TurnInput) -> SafetyState:
        return self._raw_red_flag_detector.detect(turn_input.message)

    def assess_extraction(self, extraction_payload: ExtractionPayload) -> SafetyState:
        checked_sources = []
        if extraction_payload.extraction_result is not None:
            checked_sources.append("extraction_result")
        if extraction_payload.case_update_bridge is not None:
            checked_sources.append("normalized_extraction")
        elif extraction_payload.extracted_fields:
            checked_sources.append("normalized_extraction")

        return SafetyState(
            checked_sources=checked_sources,
            trace_notes=["extraction_safety_scaffold"],
        )

    def assess_case(self, medical_case: MedicalCase | None) -> SafetyState:
        checked_sources = []
        if medical_case is not None:
            checked_sources.append("medical_case")

        return SafetyState(
            checked_sources=checked_sources,
            trace_notes=["case_safety_scaffold"],
        )
