from careena_pipeline3.models.turn import TurnContext


class ConfirmationManager:
    """Placeholder for the optional confirmation workflow."""

    def should_request_confirmation(self, context: TurnContext) -> bool:
        return False
