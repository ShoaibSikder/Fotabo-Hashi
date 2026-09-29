import json
import logging


class JsonFormatter(logging.Formatter):
    """Render only safe operational metadata as one JSON log record."""

    def format(self, record):
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, self.datefmt),
        }
        for field in ("request_id", "method", "path", "status_code"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, default=str)
