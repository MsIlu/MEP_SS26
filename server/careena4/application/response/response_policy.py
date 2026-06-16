from careena4.models.turn import TurnDecision


class ResponsePolicy:
    def response_mode_for(self, *, decision: TurnDecision) -> str:
        return decision.response_mode
