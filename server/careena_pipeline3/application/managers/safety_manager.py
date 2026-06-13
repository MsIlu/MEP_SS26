from careena_pipeline3.models.turn import ExtractionPayload, SafetyState, TurnInput
from careena_pipeline3.models.domain import MedicalCase


class SafetyManager:
    """Runs turn-level safety checks for raw and normalized inputs."""

    def assess_raw_message(self, turn_input: TurnInput) -> SafetyState:
        return SafetyState(
            checked_sources=["raw_message"],
            trace_notes=["raw_safety_scaffold"],
        )

    def assess_extraction(self, extraction_payload: ExtractionPayload) -> SafetyState:
        checked_sources = []
        if extraction_payload.case_update_bridge is not None:
            checked_sources.append("case_update_bridge")
        elif extraction_payload.extracted_fields:
            checked_sources.append("normalized_extraction")
        elif extraction_payload.extraction_result is not None:
            checked_sources.append("diagnostic_extraction_result")

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
