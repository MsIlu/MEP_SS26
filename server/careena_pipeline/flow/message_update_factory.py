from careena_pipeline.models import (
    IntentGateway,
    MessageIntentSignals,
    MessagePlannerHints,
    MessageRequirementHints,
    MessageStagingHints,
    MessageTraceSignals,
    MessageUpdate,
    StagedFollowupAnswer,
)
from careena_pipeline.planning.requirement_state import PendingFollowupContext


def build_pending_followup_update(
    *,
    text: str,
    pending_followup: PendingFollowupContext,
    request_recommendation: bool,
    mark_resolved: bool,
    staged_followup_answers: list[StagedFollowupAnswer] | None = None,
) -> MessageUpdate:
    return MessageUpdate.from_parts(
        raw_text=text,
        intent_signals=MessageIntentSignals(
            intent_category=None,
            is_medical=True,
            extraction_required=True,
            intent_confidence=0.0,
            message_role="answer_to_followup",
            possible_new_topic=False,
        ),
        requirement_hints=MessageRequirementHints(
            active_modules=list(pending_followup.active_modules),
            required_fields=list(pending_followup.required_fields),
            resolved_fields=(
                [pending_followup.resolved_field]
                if mark_resolved and pending_followup.resolved_field is not None
                else []
            ),
        ),
        planner_hints=MessagePlannerHints(
            recommended_modules=[
                "recommendation_readiness",
                "routing_recommendation",
            ],
            recommendation_requested=request_recommendation,
        ),
        trace_signals=MessageTraceSignals(
            notes=[],
            intent_gateway=None,
            llm_intent_category=None,
            llm_is_medical=None,
            llm_extraction_required=None,
            llm_message_role=None,
        ),
        staging_hints=MessageStagingHints(
            staged_followup_answers=list(staged_followup_answers or []),
            clear_staged_followup_answers=False,
        ),
    )


def build_intent_gateway_update(
    *,
    text: str,
    intent_gateway: IntentGateway,
    request_recommendation: bool,
) -> MessageUpdate:
    return MessageUpdate.from_parts(
        raw_text=text,
        intent_signals=MessageIntentSignals(
            intent_category=intent_gateway.category,
            is_medical=intent_gateway.is_medical,
            extraction_required=intent_gateway.extraction_required,
            intent_confidence=0.0,
            message_role=intent_gateway.message_role,
            possible_new_topic=False,
        ),
        planner_hints=MessagePlannerHints(
            recommended_modules=[],
            recommendation_requested=request_recommendation,
        ),
        trace_signals=MessageTraceSignals(
            notes=[],
            intent_gateway=intent_gateway,
            llm_intent_category=None,
            llm_is_medical=None,
            llm_extraction_required=None,
            llm_message_role=None,
        ),
    )


def early_response_mode_for(intent_gateway: IntentGateway) -> str:
    if intent_gateway.category in {"smalltalk", "not_medical"}:
        return "out_of_scope"
    return "cannot_assess"
