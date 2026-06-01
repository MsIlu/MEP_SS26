from careena_pipeline.observability import log_json
from careena_pipeline.models import MedicalCase, SafetyResult
from careena_pipeline.safety import SafetyGate


class StructuredSafetyStep:
    """Runs the case-aware safety assessment after parsing succeeded."""

    def __init__(self, safety_gate: SafetyGate):
        self.safety_gate = safety_gate

    def assess(self, *, text: str, case: MedicalCase) -> SafetyResult:
        structured_safety = self.safety_gate.evaluate(
            raw_text=text,
            case=case,
        )
        log_json("SAFETY STRUCTURED", structured_safety)
        return structured_safety
