import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel


LOGGER_NAME = "careena_pipeline3"
logger = logging.getLogger(LOGGER_NAME)
SIMULATION_LOGGER_NAME = "careena_pipeline3.simulation"
simulation_logger = logging.getLogger(SIMULATION_LOGGER_NAME)
DEBUG_LOG_PATH = Path(__file__).resolve().parent / "logs" / "debug_log_pipeline3.txt"
SIMULATION_LOG_PATH = (
    Path(__file__).resolve().parent / "logs" / "debug_log_simulation3.txt"
)
LOG_ARCHIVE_DIR = Path(__file__).resolve().parent / "logs" / "archive"
_startup_logs_archived = False


class _ExcludeSimulationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.name.startswith(SIMULATION_LOGGER_NAME)


def configure_debug_logging() -> None:
    global _startup_logs_archived
    _configure_console_encoding()

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

    if not _startup_logs_archived:
        _archive_existing_log(DEBUG_LOG_PATH, archive_type="pipeline")
        _archive_existing_log(SIMULATION_LOG_PATH, archive_type="simulation")
        _startup_logs_archived = True

    if not any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == DEBUG_LOG_PATH
        for handler in logger.handlers
    ):
        DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            DEBUG_LOG_PATH,
            mode="a",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        file_handler.addFilter(_ExcludeSimulationFilter())
        logger.addHandler(file_handler)

    if not any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == SIMULATION_LOG_PATH
        for handler in simulation_logger.handlers
    ):
        SIMULATION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        simulation_handler = logging.FileHandler(
            SIMULATION_LOG_PATH,
            mode="a",
            encoding="utf-8",
        )
        simulation_handler.setLevel(logging.DEBUG)
        simulation_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        simulation_logger.addHandler(simulation_handler)

    logger.setLevel(logging.DEBUG)
    simulation_logger.setLevel(logging.DEBUG)

    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def log_json(title: str, value: Any) -> None:
    if not logger.isEnabledFor(logging.DEBUG):
        return

    logger.debug("%s:\n%s", title, _to_pretty_json(value))


def log_simulation_json(title: str, value: Any) -> None:
    if not simulation_logger.isEnabledFor(logging.DEBUG):
        return

    simulation_logger.debug("%s:\n%s", title, _to_pretty_json(value))


def log_simulation_text(title: str, text: str) -> None:
    if not simulation_logger.isEnabledFor(logging.DEBUG):
        return

    simulation_logger.debug("%s:\n%s", title, text)


def _archive_existing_log(path: Path, *, archive_type: str) -> None:
    if not path.exists() or path.stat().st_size == 0:
        return

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_dir = LOG_ARCHIVE_DIR / archive_type
    archive_dir.mkdir(parents=True, exist_ok=True)
    archived_path = archive_dir / f"{path.stem}-{timestamp}{path.suffix}"
    path.rename(archived_path)


def _configure_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _to_pretty_json(value: Any) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump()

    return json.dumps(
        value,
        indent=2,
        ensure_ascii=False,
        default=str,
    )
