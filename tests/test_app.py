import json
import re

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app


def test_chat_propagates_context_and_scrubs_logs(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)
    payload = {
        "user_id": "student@vinuni.edu.vn",
        "session_id": "session-1",
        "feature": "qa",
        "message": "Refund for card 4111 1111 1111 1111?",
    }

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": "request-from-client"},
            json=payload,
        )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "request-from-client"
    assert float(response.headers["x-response-time-ms"]) >= 0
    assert response.json()["correlation_id"] == "request-from-client"

    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    api_records = [record for record in records if record.get("service") == "api"]
    assert api_records
    assert all(record["correlation_id"] == "request-from-client" for record in api_records)
    assert all(
        {"user_id_hash", "session_id", "feature", "model", "env"}.issubset(record)
        for record in api_records
    )
    assert "student@" not in json.dumps(records)
    assert "4111" not in json.dumps(records)


def test_middleware_generates_request_id() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    request_id = response.headers["x-request-id"]
    assert re.fullmatch(r"req-[0-9a-f]{8}", request_id)


def test_dashboard_contains_all_six_panels() -> None:
    with TestClient(app) as client:
        response = client.get("/dashboard")

    assert response.status_code == 200
    assert response.text.count('class="panel"') == 6
    assert "Auto refresh every 20 seconds" in response.text
    assert "P95 SLO 3,000 ms" in response.text


def test_tool_failure_is_recorded_with_request_context(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "incident-logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)
    payload = {
        "user_id": "incident-user",
        "session_id": "incident-session",
        "feature": "qa",
        "message": "Explain monitoring",
    }

    with TestClient(app, raise_server_exceptions=False) as client:
        client.post("/incidents/tool_fail/enable")
        try:
            response = client.post("/chat", json=payload)
        finally:
            client.post("/incidents/tool_fail/disable")

    assert response.status_code == 500
    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    failure = next(record for record in records if record.get("event") == "request_failed")
    assert failure["error_type"] == "RuntimeError"
    assert failure["session_id"] == "incident-session"
    assert re.fullmatch(r"req-[0-9a-f]{8}", failure["correlation_id"])
