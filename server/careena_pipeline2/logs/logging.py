import json
import logging
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel


LOGGER_NAME = "careena_pipeline2"
logger = logging.getLogger(LOGGER_NAME)
LOG_PATH = Path(__file__).resolve().parent / "debug_log_pipeline2.txt"


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
    if not any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == LOG_PATH
        for handler in logger.handlers
    ):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            LOG_PATH,
            mode="a",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)


def log_json(title: str, value: Any) -> None:
    if not logger.isEnabledFor(logging.DEBUG):
        return
    logger.debug("%s:\n%s", title, _to_pretty_json(value))


def log_pipeline_outcome(result: Any) -> None:
    if not logger.isEnabledFor(logging.DEBUG):
        return

    summary = {
        "response_mode": getattr(result, "response_mode", None),
        "followup_question": getattr(result, "followup_question", None),
        "safety": _dump(getattr(result, "safety", None)),
        "readiness": _dump(getattr(result, "readiness", None)),
        "recommendation": _dump(getattr(result, "recommendation", None)),
        "dialogue_state": _dump(getattr(result, "dialogue_state", None)),
        "message_update": _dump(getattr(result, "message_update", None)),
        "case": _dump(getattr(result, "case", None)),
    }
    log_json("PIPELINE OUTCOME", summary)


def _dump(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    return value


def _to_pretty_json(value: Any) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump()
    return json.dumps(
        value,
        indent=2,
        ensure_ascii=False,
        default=str,
    )
