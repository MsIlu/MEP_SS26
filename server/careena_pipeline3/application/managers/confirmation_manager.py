from careena_pipeline3.models.turn import ConfirmationDecision, TurnContext


class ConfirmationManager:
    """
    Placeholder for the optional confirmation workflow.

    The manager currently returns an explicit decision contract so the
    `DialogueManager` can keep confirmation as a visible late-stage boundary
    without pretending the feature is already fully implemented.

    Intended direction:
    confirmation should later receive user-visible candidate facts or
    structured edits, collect user confirmation or correction, and route that
    feedback back through `DialogueManager` into the canonical case-update
    path instead of mutating case truth on its own.
    """

    def evaluate(self, context: TurnContext) -> ConfirmationDecision:
        return ConfirmationDecision(
            should_request_confirmation=False,
            trace_notes=["confirmation_placeholder"],
        )
