from typing import Literal, Optional

from extraction.models.system.baseSchema import BaseSchema

"""
Author @Freddy
    Contextual metadata for an ObservationEvent.

    Captures:
    - negation (e.g. "no pain")
    - certainty level (confirmed / suspected / uncertain)
    - temporality (when applicable)
"""
class ObservationContext(BaseSchema):
    negated: bool = False
    certainty: Literal["confirmed", "suspected", "uncertain"] = "confirmed"
    temporality: Optional[str] = None

"""
Author @Freddy
    Atomic structured medical observation extracted from text.

    Represents a single clinically relevant element such as:
    - symptom
    - medication
    - diagnosis

    Includes:
    - source span (exact text reference)
    - normalized label
    - contextual modifiers (negation, certainty, temporality)
"""
class ObservationEvent(BaseSchema):
    id: str
    type: Literal["symptom", "medication", "diagnosis"]

    label: str
    source_span: str

    context: ObservationContext