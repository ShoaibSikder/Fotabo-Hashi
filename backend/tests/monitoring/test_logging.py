import json
import logging
from types import SimpleNamespace

from infrastructure.logging.filters import RequestIDFilter
from infrastructure.logging.formatters import JsonFormatter


def test_json_formatter_emits_safe_structured_metadata():
    record = logging.LogRecord(
        "apps.example", logging.INFO, "", 0, "Request completed", (), None
    )
    record.request_id = "request-123"
    record.method = "GET"
    record.path = "/api/v1/health/live/"
    record.status_code = 200

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["message"] == "Request completed"
    assert payload["request_id"] == "request-123"
    assert "authorization" not in payload
    assert "cookie" not in payload


def test_request_id_filter_uses_request_metadata_only():
    record = logging.LogRecord("apps.example", logging.INFO, "", 0, "message", (), None)
    record.request = SimpleNamespace(
        request_id="request-456",
        method="POST",
        path="/api/v1/blood-requests/",
    )

    assert RequestIDFilter().filter(record)
    assert record.request_id == "request-456"
    assert record.method == "POST"
