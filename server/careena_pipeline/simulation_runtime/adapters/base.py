from typing import Protocol

from careena_pipeline.simulation_runtime.models import (
    SimulationSystemTurn,
    SimulationTranscriptEntry,
)


class ConversationSystemAdapter(Protocol):
    def respond(
        self,
        *,
        user_message: str,
        transcript: list[SimulationTranscriptEntry],
        state,
    ) -> SimulationSystemTurn:
        """Returns one system turn for the incoming user message."""
