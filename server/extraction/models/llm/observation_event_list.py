from typing import List
from extraction.models.llm.observation_event import ObservationEvent
from extraction.models.system.baseSchema import BaseSchema

"""
Author @Freddy
    Container for multiple ObservationEvent objects.

    Represents all extracted medical observations
    from a single input text.
"""
class ObservationEventList(BaseSchema):
    events: List[ObservationEvent]