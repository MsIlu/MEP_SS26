from typing import Protocol

from careena4.simulation_runtime.models import SimulationSystemTurn, SimulationTranscriptEntry


class ConversationSystemAdapter(Protocol):
    def respond(
        self,
        *,
        user_message: str,
        transcript: list[SimulationTranscriptEntry],
        state,
    ) -> SimulationSystemTurn:
        ...
