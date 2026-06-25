import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel


RAW_LOGGER_NAME = "careena4.raw"
logger = logging.getLogger(RAW_LOGGER_NAME)
SIMULATION_RAW_LOGGER_NAME = "careena4.simulation.raw"
simulation_logger = logging.getLogger(SIMULATION_RAW_LOGGER_NAME)
EVENT_LOGGER_NAME = "careena4.events"
event_logger = logging.getLogger(EVENT_LOGGER_NAME)
DEBUG_LOG_PATH = Path(__file__).resolve().parent / "logs" / "debug_log_careena4.txt"
SIMULATION_LOG_PATH = Path(__file__).resolve().parent / "logs" / "debug_log_simulation4.txt"
EVENT_LOG_PATH = Path(__file__).resolve().parent / "logs" / "event_log_careena4.txt"
LOG_ARCHIVE_DIR = Path(__file__).resolve().parent / "logs" / "archive"
_startup_logs_archived = False


class _ExcludeSimulationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.name.startswith("careena4.simulation")


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
        _archive_existing_log(EVENT_LOG_PATH, archive_type="pipeline_events")
        _startup_logs_archived = True

    _ensure_file_handler(
        target_logger=logger,
        path=DEBUG_LOG_PATH,
        level=logging.DEBUG,
        formatter=logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
        log_filter=_ExcludeSimulationFilter(),
    )
    _ensure_file_handler(
        target_logger=simulation_logger,
        path=SIMULATION_LOG_PATH,
        level=logging.DEBUG,
        formatter=logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
    )
    _ensure_file_handler(
        target_logger=event_logger,
        path=EVENT_LOG_PATH,
        level=logging.INFO,
        formatter=logging.Formatter("%(message)s"),
    )

    logger.setLevel(logging.DEBUG)
    simulation_logger.setLevel(logging.DEBUG)
    event_logger.setLevel(logging.INFO)
    logger.propagate = True
    simulation_logger.propagate = True
    event_logger.propagate = False

    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def log_json(title: str, value: Any) -> None:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("%s:\n%s", title, _to_pretty_json(value))


def log_simulation_json(title: str, value: Any) -> None:
    if simulation_logger.isEnabledFor(logging.DEBUG):
        simulation_logger.debug("%s:\n%s", title, _to_pretty_json(value))


def log_simulation_text(title: str, text: str) -> None:
    if simulation_logger.isEnabledFor(logging.DEBUG):
        simulation_logger.debug("%s:\n%s", title, text)


def log_event(event: str, *, level: int = logging.INFO, **fields: Any) -> None:
    if event_logger.isEnabledFor(level):
        event_logger.log(level, _to_event_text(_build_event_record(event, fields)))


def _archive_existing_log(path: Path, *, archive_type: str) -> None:
    if not path.exists() or path.stat().st_size == 0:
        return
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_dir = LOG_ARCHIVE_DIR / archive_type
    archive_dir.mkdir(parents=True, exist_ok=True)
    path.rename(archive_dir / f"{path.stem}-{timestamp}{path.suffix}")


def _configure_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _ensure_file_handler(
    *,
    target_logger: logging.Logger,
    path: Path,
    level: int,
    formatter: logging.Formatter,
    log_filter: logging.Filter | None = None,
) -> None:
    if any(
        isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == path
        for handler in target_logger.handlers
    ):
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(path, mode="a", encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(formatter)
    if log_filter is not None:
        handler.addFilter(log_filter)
    target_logger.addHandler(handler)


def _build_event_record(event: str, fields: dict[str, Any]) -> dict[str, Any]:
    record = {"ts": datetime.utcnow().isoformat(timespec="milliseconds") + "Z", "event": event}
    for key, value in fields.items():
        if value is not None:
            record[key] = _json_ready(value)
    return record


def _json_ready(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_ready(item) for item in value]
    return value


def _to_pretty_json(value: Any) -> str:
    return json.dumps(_json_ready(value), indent=2, ensure_ascii=False, default=str)


def _to_event_text(value: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, raw_item in value.items():
        item = _json_ready(raw_item)
        rendered = json.dumps(item, ensure_ascii=False, default=str) if isinstance(item, (dict, list)) else str(item)
        parts.append(f"{key}={rendered}")
    return " | ".join(parts)
