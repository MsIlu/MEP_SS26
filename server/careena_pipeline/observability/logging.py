import json
import logging
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from careena_pipeline.planning.requirement_state import requirement_key, requirement_keys

logger = logging.getLogger("careena_pipeline")
testrun_logger = logging.getLogger("careena_pipeline.testrun")
PIPELINE_DEBUG_LOG_PATH = (
    Path(__file__).resolve().parent
    / "logs"
    / "debug_log_pipeline.txt"
)
TESTRUN_DEBUG_LOG_PATH = (
    Path(__file__).resolve().parent
    / "logs"
    / "debug_log_testrun.txt"
)


class _ExcludeTestrunFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.name.startswith("careena_pipeline.testrun")


def configure_debug_logging() -> None:
    _configure_console_encoding()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    _configure_file_logging()

    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def _configure_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _configure_file_logging() -> None:
    if any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == PIPELINE_DEBUG_LOG_PATH
        for handler in logger.handlers
    ):
        pipeline_handler_exists = True
    else:
        pipeline_handler_exists = False

    if not pipeline_handler_exists:
        PIPELINE_DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            PIPELINE_DEBUG_LOG_PATH,
            mode="a",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        file_handler.addFilter(_ExcludeTestrunFilter())
        logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)

    if not any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == TESTRUN_DEBUG_LOG_PATH
        for handler in testrun_logger.handlers
    ):
        TESTRUN_DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        testrun_file_handler = logging.FileHandler(
            TESTRUN_DEBUG_LOG_PATH,
            mode="a",
            encoding="utf-8",
        )
        testrun_file_handler.setLevel(logging.DEBUG)
        testrun_file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        testrun_logger.addHandler(testrun_file_handler)

    testrun_logger.setLevel(logging.DEBUG)


def log_json(title: str, value: Any) -> None:
    if not logger.isEnabledFor(logging.DEBUG):
        return

    logger.debug("%s:\n%s", title, _to_pretty_json(value))


def log_testrun_json(title: str, value: Any) -> None:
    if not testrun_logger.isEnabledFor(logging.DEBUG):
        return

    testrun_logger.debug("%s:\n%s", title, _to_pretty_json(value))


def log_testrun_response(title: str, response: dict[str, Any]) -> None:
    if not testrun_logger.isEnabledFor(logging.DEBUG):
        return

    lines = [f"{title}:"]

    text = response.get("response")
    if isinstance(text, str):
        lines.append("response:")
        lines.append(text)

    for key, value in response.items():
        if key == "response":
            continue
        lines.append(f"{key}: {_to_pretty_json(value)}")

    testrun_logger.debug("\n".join(lines))


def log_pipeline_outcome(result: Any) -> None:
    if not logger.isEnabledFor(logging.DEBUG):
        return

    case = getattr(result, "case", None)
    readiness = getattr(result, "readiness", None)
    gate = getattr(result, "recommendation_gate", None)
    recommendation = getattr(result, "recommendation", None)
    safety = getattr(result, "safety", None)
    dialogue_state = getattr(result, "dialogue_state", None)
    message_update = getattr(result, "message_update", None)

    summary = {
        "response_mode": getattr(result, "response_mode", None),
        "red_flag_detected": getattr(safety, "red_flag_detected", None),
        "case": _case_summary(case),
        "dialogue_state": _dialogue_summary(dialogue_state),
        "message_update": _message_update_summary(message_update),
        "readiness": _readiness_summary(readiness),
        "gate": _gate_summary(gate),
        "recommendation": _recommendation_summary(recommendation),
    }
    log_json("PIPELINE OUTCOME", summary)


def log_case_snapshot(case: Any) -> None:
    if not logger.isEnabledFor(logging.DEBUG):
        return

    log_json("CASE SNAPSHOT", _case_summary(case))


def _to_pretty_json(value: Any) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump()

    return json.dumps(
        value,
        indent=2,
        ensure_ascii=False,
        default=str,
    )


def _case_summary(case: Any) -> dict[str, Any] | None:
    if case is None:
        return None

    ensure_primary_problem = getattr(case, "ensure_primary_problem", None)
    if callable(ensure_primary_problem):
        ensure_primary_problem()

    observations = getattr(case, "observations", []) or []
    primary_focus_label = getattr(case, "primary_focus_label", None)
    active_problem_ids = getattr(case, "active_problem_ids", None)
    focus = primary_focus_label() if callable(primary_focus_label) else None
    return {
        "case_id": getattr(case, "case_id", None),
        "subject": _dump(getattr(case, "subject", None)),
        "active_problem_ids": active_problem_ids() if callable(active_problem_ids) else [],
        "primary_problem_id": getattr(case, "primary_problem_id", None),
        "primary_focus": focus,
        "observations": [
            {
                "type": getattr(observation, "type", None),
                "label": getattr(observation, "label", None),
                "display_label": getattr(observation, "display_label", None),
                "concept": getattr(observation, "concept", None),
                "body_site": observation.runtime_value("body_site"),
                "laterality": getattr(observation, "laterality", None),
                "course": observation.runtime_value("course"),
                "measurement": getattr(observation, "measurement", {}),
                "subject_ref": getattr(observation, "subject_ref", None),
                "temporality": observation.runtime_value("temporality"),
                "severity": observation.runtime_value("severity"),
                "details": getattr(observation, "details", {}),
                "negated": getattr(observation, "negated", None),
                "status": getattr(observation, "status", None),
            }
            for observation in observations
        ],
    }


def _readiness_summary(readiness: Any) -> dict[str, Any] | None:
    if readiness is None:
        return None

    return {
        "ready": getattr(readiness, "ready", None),
        "missing_information": getattr(readiness, "missing_information", []),
        "blocking_requirements": getattr(readiness, "blocking_requirements", []),
        "reason_tags": getattr(readiness, "reason_tags", []),
        "confidence_gaps": getattr(readiness, "confidence_gaps", []),
        "disambiguation_needed": getattr(readiness, "disambiguation_needed", None),
        "confirmation_needed": getattr(readiness, "confirmation_needed", None),
    }


def _gate_summary(gate: Any) -> dict[str, Any] | None:
    if gate is None:
        return None

    return {
        "action": getattr(gate, "action", None),
        "question": getattr(gate, "question", None),
        "missing_information": getattr(gate, "missing_information", []),
        "reasons": getattr(gate, "reasons", []),
        "activated_modules": getattr(gate, "activated_modules", []),
    }


def _recommendation_summary(recommendation: Any) -> dict[str, Any] | None:
    if recommendation is None:
        return None

    return {
        "care_level": getattr(recommendation, "care_level", None),
        "urgency_level": getattr(recommendation, "urgency_level", None),
        "specialty": getattr(recommendation, "specialty", None),
        "urgency": getattr(recommendation, "urgency", None),
        "confidence": getattr(recommendation, "confidence", None),
        "reasoning_tags": getattr(recommendation, "reasoning_tags", []),
        "reasons": getattr(recommendation, "reasons", []),
    }


def _dump(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    return value


def _dialogue_summary(dialogue_state: Any) -> dict[str, Any] | None:
    if dialogue_state is None:
        return None

    return {
        "conversation_id": getattr(dialogue_state, "conversation_id", None),
        "active_case_id": getattr(dialogue_state, "active_case_id", None),
        "focus_observation_id": getattr(dialogue_state, "focus_observation_id", None),
        "focus_label": getattr(dialogue_state, "focus_label", None),
        "current_topic_status": getattr(dialogue_state, "current_topic_status", None),
        "last_question_key": getattr(dialogue_state, "last_question_key", None),
        "active_modules": getattr(dialogue_state, "active_modules", []),
        "open_requirements": requirement_keys(
            getattr(dialogue_state, "open_requirements", [])
        ),
        "resolved_requirements": requirement_keys(
            getattr(dialogue_state, "resolved_requirements", [])
        ),
        "pending_followup": requirement_key(
            getattr(dialogue_state, "pending_followup", None)
        ),
        "awaiting_confirmation": getattr(dialogue_state, "awaiting_confirmation", None),
        "recommendation_requested": getattr(dialogue_state, "recommendation_requested", None),
        "recommended_modules": getattr(dialogue_state, "recommended_modules", []),
    }


def _message_update_summary(message_update: Any) -> dict[str, Any] | None:
    if message_update is None:
        return None

    case_payload = getattr(message_update, "case_payload", None)
    requirement_hints = getattr(message_update, "requirement_hints", None)
    planner_hints = getattr(message_update, "planner_hints", None)

    return {
        "intent_category": getattr(message_update, "intent_category", None),
        "gateway_category": getattr(message_update, "gateway_category", None),
        "llm_intent_category": getattr(message_update, "llm_intent_category", None),
        "message_role": getattr(message_update, "message_role", None),
        "gateway_message_role": getattr(message_update, "gateway_message_role", None),
        "llm_message_role": getattr(message_update, "llm_message_role", None),
        "is_medical": getattr(message_update, "is_medical", None),
        "llm_is_medical": getattr(message_update, "llm_is_medical", None),
        "extraction_required": getattr(message_update, "extraction_required", None),
        "gateway_extraction_required": getattr(
            message_update,
            "gateway_extraction_required",
            None,
        ),
        "llm_extraction_required": getattr(
            message_update,
            "llm_extraction_required",
            None,
        ),
        "possible_new_topic": getattr(message_update, "possible_new_topic", None),
        "user_requests_recommendation": getattr(
            message_update,
            "user_requests_recommendation",
            None,
        ),
        "active_modules": (
            list(requirement_hints.active_modules)
            if requirement_hints is not None
            else getattr(message_update, "active_modules", [])
        ),
        "required_fields": requirement_keys(
            (
                requirement_hints.required_fields
                if requirement_hints is not None
                else getattr(message_update, "required_fields", [])
            )
        ),
        "resolved_fields": requirement_keys(
            (
                requirement_hints.resolved_fields
                if requirement_hints is not None
                else getattr(message_update, "resolved_fields", [])
            )
        ),
        "recommended_modules": (
            list(planner_hints.recommended_modules)
            if planner_hints is not None
            else getattr(message_update, "recommended_modules", [])
        ),
        "has_case_payload": (
            case_payload.has_updates
            if case_payload is not None
            else None
        ),
    }
