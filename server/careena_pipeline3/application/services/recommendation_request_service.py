from careena_pipeline3.models.workflow import IntentGateway


class RecommendationRequestService:
    """
    Reads explicit recommendation-request intent from Call 1.
    """

    def is_requested(
        self,
        text: str,
        *,
        gateway: IntentGateway | None = None,
    ) -> bool:
        if gateway is None:
            return False
        return (
            gateway.message_role == "recommendation_request"
            or gateway.signals.recommendation_request
        )
