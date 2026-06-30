from __future__ import annotations

from careena4.models.interpretation import TurnInterpretation
from careena4.models.understanding import CurrentTurnUnderstanding, StsConsultationReasonCandidate


def to_current_turn_understanding(
    *,
    raw_message: str,
    interpretation: TurnInterpretation,
    sts_matches: list[StsConsultationReasonCandidate] | None = None,
    no_match_reason: str | None = None,
) -> CurrentTurnUnderstanding | None:
    signal = interpretation.current_turn_understanding
    if signal is None:
        return None
    resolved_sts_matches = list(sts_matches or [])

    trace_notes = list(signal.trace_notes)
    trace_notes.extend(
        [
            f"turn_interpretation:symptoms:{len(signal.symptoms)}",
            f"turn_interpretation:sts_matches:{len(resolved_sts_matches)}",
        ]
    )
    return CurrentTurnUnderstanding(
        raw_message=raw_message,
        symptoms=[symptom.model_copy(deep=True) for symptom in signal.symptoms],
        sts_matches=[match.model_copy(deep=True) for match in resolved_sts_matches],
        no_match_reason=no_match_reason,
        trace_notes=trace_notes,
    )
