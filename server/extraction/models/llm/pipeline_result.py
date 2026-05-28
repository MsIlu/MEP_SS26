from extraction.models.llm.intent import MedicalIntent
from extraction.models.llm.observation_event_list import ObservationEventList
from extraction.models.system.baseSchema import BaseSchema

"""
Author @Freddy
    Final output container of the extraction pipeline.

    Combines:
    - intent classification result
    - optionally extracted observations

    Represents the full structured interpretation of input text.
"""
class PipelineResult(BaseSchema):

    intent: MedicalIntent

    observations: ObservationEventList | None = None