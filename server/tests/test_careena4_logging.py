import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import BaseModel

import careena4.server_log.logging as careena_logging
from careena4.core.engine import ExtractionEngine


def _snapshot_logger_state() -> dict[str, dict[str, object]]:
    tracked_loggers = {
        "package": careena_logging.package_logger,
        "raw": careena_logging.logger,
        "simulation": careena_logging.simulation_logger,
        "event": careena_logging.event_logger,
    }
    return {
        key: {
            "logger": target_logger,
            "handlers": list(target_logger.handlers),
            "level": target_logger.level,
            "propagate": target_logger.propagate,
        }
        for key, target_logger in tracked_loggers.items()
    }


def _restore_logger_state(snapshot: dict[str, dict[str, object]]) -> None:
    for state in snapshot.values():
        target_logger = state["logger"]
        for handler in list(target_logger.handlers):
            target_logger.removeHandler(handler)
            if handler not in state["handlers"]:
                handler.close()
        for handler in state["handlers"]:
            target_logger.addHandler(handler)
        target_logger.setLevel(state["level"])
        target_logger.propagate = state["propagate"]


def _flush_handlers(*target_loggers: logging.Logger) -> None:
    seen_handler_ids: set[int] = set()
    for target_logger in target_loggers:
        for handler in target_logger.handlers:
            handler_id = id(handler)
            if handler_id in seen_handler_ids:
                continue
            seen_handler_ids.add(handler_id)
            flush = getattr(handler, "flush", None)
            if callable(flush):
                flush()


class Careena4LoggingTests(unittest.TestCase):
    def test_pipeline_debug_logging_captures_package_debug_records(self):
        snapshot = _snapshot_logger_state()

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            try:
                with (
                    patch.object(careena_logging, "DEBUG_LOG_PATH", tmp_path / "debug_log_careena4.txt"),
                    patch.object(careena_logging, "SIMULATION_LOG_PATH", tmp_path / "debug_log_simulation4.txt"),
                    patch.object(careena_logging, "EVENT_LOG_PATH", tmp_path / "event_log_careena4.txt"),
                    patch.object(careena_logging, "LOG_ARCHIVE_DIR", tmp_path / "archive"),
                    patch.object(careena_logging, "_startup_logs_archived", False),
                ):
                    careena_logging.configure_debug_logging()

                    logging.getLogger("careena4.core.engine").debug("package-debug-check")
                    careena_logging.log_json("HTTP /chatscreen RESPONSE", {"ok": True})
                    careena_logging.log_simulation_text("SIMULATION TRACE", "simulation-only")
                    careena_logging.log_event("careena4.test.event", layer="test")

                    _flush_handlers(
                        careena_logging.package_logger,
                        careena_logging.logger,
                        careena_logging.simulation_logger,
                        careena_logging.event_logger,
                    )

                    debug_text = careena_logging.DEBUG_LOG_PATH.read_text(encoding="utf-8")
                    simulation_text = careena_logging.SIMULATION_LOG_PATH.read_text(encoding="utf-8")
                    event_text = careena_logging.EVENT_LOG_PATH.read_text(encoding="utf-8")

                    self.assertIn("package-debug-check", debug_text)
                    self.assertIn("HTTP /chatscreen RESPONSE", debug_text)
                    self.assertNotIn("careena4.test.event", debug_text)
                    self.assertNotIn("simulation-only", debug_text)
                    self.assertIn("simulation-only", simulation_text)
                    self.assertIn("careena4.test.event", event_text)
            finally:
                _restore_logger_state(snapshot)

    def test_extraction_engine_logs_validated_json_payload(self):
        class DemoSchema(BaseModel):
            answer: str
            score: int

        class FakeLLMClient:
            default_model = "fake-model"

            def complete(self, **kwargs):
                return '{"answer":"ok","score":2}'

        engine = ExtractionEngine(FakeLLMClient())

        with patch("careena4.core.engine.log_json") as log_json_mock:
            result = engine.extract(
                text="payload",
                system_prompt="prompt",
                output_schema=DemoSchema,
                call_name="demo_call",
                prompt_name="demo_prompt",
                prompt_version="2026-06-24.1",
            )

        self.assertEqual(result.answer, "ok")
        self.assertEqual(result.score, 2)
        log_json_mock.assert_called_once_with(
            "llm_validated_json:demo_call:DemoSchema",
            {"answer": "ok", "score": 2},
        )


if __name__ == "__main__":
    unittest.main()
