import importlib.util
from pathlib import Path

import pytest


fastapi = pytest.importorskip("fastapi")
pytest.importorskip("fastapi.testclient")

from fastapi.testclient import TestClient


def _load_api_module():
    module_path = Path(__file__).resolve().parents[1] / "careena4.py"
    spec = importlib.util.spec_from_file_location("careena4_http_shell", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_http_shell_keeps_chat_contract_keys():
    module = _load_api_module()
    client = TestClient(module.app)

    session_response = client.post("/session")
    session_id = session_response.json()["session_id"]

    response = client.post(
        "/chatscreen",
        json={"message": "Ich habe Bauchschmerzen.", "session_id": session_id},
    )

    payload = response.json()
    assert payload.keys() >= {
        "response",
        "response_mode",
        "red_flag",
        "trace_notes",
        "pending_followup",
        "recommendation_requested",
        "recommendation_ready",
        "recommendation_result",
    }


def test_case_endpoint_returns_new_debug_state_shape():
    module = _load_api_module()
    client = TestClient(module.app)

    session_response = client.post("/session")
    session_id = session_response.json()["session_id"]
    client.post(
        "/chatscreen",
        json={"message": "Ich habe seit gestern Bauchschmerzen.", "session_id": session_id},
    )

    response = client.get(f"/case/{session_id}")
    payload = response.json()

    assert payload.keys() >= {
        "case",
        "case_topic",
        "conversation_state",
        "recommendation_state",
    }
